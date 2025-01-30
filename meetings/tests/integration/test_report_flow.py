from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient
from ...models.reports import Report, ReportExecution
from ...models.meetings import Meeting
from ...services.report_service import ReportService
from ...services.email_service import EmailService
from django.utils import timezone
from datetime import timedelta
import json

User = get_user_model()

class ReportFlowTest(TestCase):
    """Rapor akış testleri"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Test verileri oluştur
        self.create_test_data()
        
    def create_test_data(self):
        """Test verilerini oluştur"""
        now = timezone.now()
        
        # Toplantılar oluştur
        for i in range(10):
            Meeting.objects.create(
                title=f'Meeting {i}',
                start_time=now - timedelta(days=i),
                end_time=now - timedelta(days=i) + timedelta(hours=1),
                status=Meeting.StatusTypes.COMPLETED,
                organizer=self.user
            )
    
    def test_complete_report_flow(self):
        """Tam rapor akışı testi"""
        
        # 1. Rapor oluştur
        report_data = {
            'title': 'Monthly Report',
            'report_type': Report.ReportTypes.MEETING_SUMMARY,
            'start_date': (timezone.now() - timedelta(days=30)).date().isoformat(),
            'end_date': timezone.now().date().isoformat(),
            'parameters': {'include_cancelled': True}
        }
        
        response = self.client.post(
            reverse('report-list'),
            report_data,
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        report_id = response.data['id']
        
        # 2. Raporu generate et
        generate_data = {
            'start_date': report_data['start_date'],
            'end_date': report_data['end_date'],
            'parameters': report_data['parameters']
        }
        
        response = self.client.post(
            reverse('report-generate', args=[report_id]),
            generate_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        execution_id = response.data['execution_id']
        
        # 3. Execution durumunu kontrol et
        response = self.client.get(
            reverse('reportexecution-detail', args=[execution_id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], ReportExecution.StatusTypes.COMPLETED)
        
        # 4. Raporu dışa aktar
        export_data = {
            'execution_id': execution_id,
            'format': 'excel'
        }
        
        response = self.client.post(
            reverse('report-export', args=[report_id]),
            export_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('file_url', response.data)
        
        # 5. Email gönderimini kontrol et
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.user.email)
        
    def test_scheduled_report_flow(self):
        """Zamanlanmış rapor akışı testi"""
        
        # 1. Zamanlanmış rapor oluştur
        report_data = {
            'title': 'Daily Report',
            'report_type': Report.ReportTypes.MEETING_SUMMARY,
            'start_date': (timezone.now() - timedelta(days=1)).date().isoformat(),
            'end_date': timezone.now().date().isoformat(),
            'is_scheduled': True,
            'schedule_frequency': 'daily',
            'parameters': {'include_cancelled': True}
        }
        
        response = self.client.post(
            reverse('report-list'),
            report_data,
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        report_id = response.data['id']
        
        # 2. Zamanlanmış raporu çalıştır
        ReportService.run_scheduled_reports()
        
        # 3. Execution'ı kontrol et
        report = Report.objects.get(id=report_id)
        execution = report.executions.latest('created_at')
        
        self.assertEqual(execution.status, ReportExecution.StatusTypes.COMPLETED)
        
        # 4. Email gönderimini kontrol et
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        
        self.assertIn('Zamanlanmış Rapor', email.subject)
        self.assertEqual(email.to[0], self.user.email)
        
    def test_report_error_flow(self):
        """Hata durumu akış testi"""
        
        # 1. Hatalı parametre ile rapor oluştur
        report_data = {
            'title': 'Error Report',
            'report_type': Report.ReportTypes.MEETING_SUMMARY,
            'start_date': 'invalid_date',
            'end_date': timezone.now().date().isoformat()
        }
        
        response = self.client.post(
            reverse('report-list'),
            report_data,
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        
        # 2. Geçersiz execution ID ile export
        report = Report.objects.create(
            title='Test Report',
            report_type=Report.ReportTypes.MEETING_SUMMARY,
            created_by=self.user
        )
        
        export_data = {
            'execution_id': 999999,
            'format': 'excel'
        }
        
        response = self.client.post(
            reverse('report-export', args=[report.id]),
            export_data,
            format='json'
        )
        self.assertEqual(response.status_code, 404)
