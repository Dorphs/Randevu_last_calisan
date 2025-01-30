from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models.reports import Report, ReportExecution, Dashboard, DashboardWidget
from datetime import datetime, timedelta

User = get_user_model()

class ReportTests(APITestCase):
    def setUp(self):
        # Test kullanıcıları oluştur
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='adminpass123',
            email='admin@example.com',
            is_staff=True
        )
        
        # Test raporu oluştur
        self.report = Report.objects.create(
            title='Test Report',
            report_type=Report.ReportTypes.MEETING_SUMMARY,
            created_by=self.user,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=7)).date()
        )
        
        # API client'ı ayarla
        self.client = APIClient()
        
    def test_create_report(self):
        """Rapor oluşturma testi"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'title': 'New Test Report',
            'report_type': Report.ReportTypes.VISITOR_ANALYTICS,
            'start_date': timezone.now().date().isoformat(),
            'end_date': (timezone.now() + timedelta(days=7)).date().isoformat(),
            'parameters': {'include_cancelled': True}
        }
        
        response = self.client.post('/api/reports/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 2)
        self.assertEqual(Report.objects.latest('id').title, 'New Test Report')
        
    def test_generate_report(self):
        """Rapor oluşturma (generate) testi"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'start_date': timezone.now().date().isoformat(),
            'end_date': (timezone.now() + timedelta(days=7)).date().isoformat(),
            'parameters': {'include_cancelled': True}
        }
        
        response = self.client.post(
            f'/api/reports/{self.report.id}/generate/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('execution_id', response.data)
        
    def test_export_report(self):
        """Rapor dışa aktarma testi"""
        self.client.force_authenticate(user=self.user)
        
        # Önce bir execution oluştur
        execution = ReportExecution.objects.create(
            report=self.report,
            status=ReportExecution.StatusTypes.COMPLETED
        )
        
        data = {
            'execution_id': execution.id,
            'format': 'excel'
        }
        
        response = self.client.post(
            f'/api/reports/{self.report.id}/export/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('file_url', response.data)
        
    def test_unauthorized_access(self):
        """Yetkisiz erişim testi"""
        response = self.client.get('/api/reports/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_permission_denied(self):
        """İzin reddedilme testi"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        self.client.force_authenticate(user=other_user)
        
        response = self.client.get(f'/api/reports/{self.report.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_rate_limiting(self):
        """Rate limiting testi"""
        self.client.force_authenticate(user=self.user)
        
        # Rate limit'i aşana kadar istek gönder
        for _ in range(11):  # Limit 10/saat
            response = self.client.post(
                f'/api/reports/{self.report.id}/generate/',
                {},
                format='json'
            )
        
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

class DashboardTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.dashboard = Dashboard.objects.create(
            title='Test Dashboard',
            owner=self.user
        )
        self.client = APIClient()
        
    def test_create_dashboard(self):
        """Dashboard oluşturma testi"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'title': 'New Dashboard',
            'layout': {'widgets': []},
            'is_public': False
        }
        
        response = self.client.post('/api/dashboards/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Dashboard.objects.count(), 2)
        
    def test_add_widget(self):
        """Widget ekleme testi"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'title': 'Test Widget',
            'widget_type': DashboardWidget.WidgetTypes.CHART,
            'data_source': {
                'type': 'meeting_summary',
                'chart_type': 'bar'
            },
            'refresh_interval': 300
        }
        
        response = self.client.post(
            f'/api/dashboards/{self.dashboard.id}/add-widget/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DashboardWidget.objects.count(), 1)
        
    def test_share_dashboard(self):
        """Dashboard paylaşım testi"""
        self.client.force_authenticate(user=self.user)
        
        other_user = User.objects.create_user(
            username='shareuser',
            password='sharepass123'
        )
        
        data = {
            'user_ids': [other_user.id]
        }
        
        response = self.client.post(
            f'/api/dashboards/{self.dashboard.id}/share/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(other_user, self.dashboard.shared_with.all())
