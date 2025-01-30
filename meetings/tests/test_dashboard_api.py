from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from ..models.reports import Dashboard, DashboardWidget
from ..services.dashboard_service import DashboardService
import json

User = get_user_model()

class DashboardAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123',
            email='other@example.com'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.dashboard = Dashboard.objects.create(
            title='Test Dashboard',
            owner=self.user
        )
        
        self.widget = DashboardWidget.objects.create(
            dashboard=self.dashboard,
            title='Test Widget',
            widget_type='MEETING_TREND',
            position={'x': 0, 'y': 0, 'w': 6, 'h': 4}
        )
        
    def test_create_dashboard(self):
        """Dashboard oluşturma testi"""
        url = reverse('dashboard-list')
        data = {
            'title': 'New Dashboard',
            'description': 'Test Description',
            'is_public': False
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Dashboard.objects.count(), 2)
        self.assertEqual(response.data['title'], 'New Dashboard')
        
    def test_list_dashboards(self):
        """Dashboard listeleme testi"""
        url = reverse('dashboard-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_share_dashboard(self):
        """Dashboard paylaşım testi"""
        url = reverse('dashboard-share', args=[self.dashboard.id])
        data = {
            'user_ids': [self.other_user.id]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.other_user, self.dashboard.shared_with.all())
        
    def test_add_widget(self):
        """Widget ekleme testi"""
        url = reverse('dashboardwidget-list')
        data = {
            'dashboard': self.dashboard.id,
            'title': 'New Widget',
            'widget_type': 'MEETING_STATUS',
            'position': {'x': 6, 'y': 0, 'w': 6, 'h': 4}
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DashboardWidget.objects.count(), 2)
        
    def test_refresh_widget(self):
        """Widget yenileme testi"""
        url = reverse('dashboardwidget-refresh', args=[self.widget.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        
    def test_update_widget_position(self):
        """Widget pozisyon güncelleme testi"""
        url = reverse('dashboardwidget-position', args=[self.widget.id])
        data = {
            'x': 1,
            'y': 1,
            'w': 4,
            'h': 3
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.widget.refresh_from_db()
        self.assertEqual(self.widget.position['x'], 1)
        
    def test_export_dashboard(self):
        """Dashboard dışa aktarma testi"""
        url = reverse('dashboard-export', args=[self.dashboard.id])
        response = self.client.post(url + '?format=excel')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('file_url', response.data)
        
    def test_unauthorized_access(self):
        """Yetkisiz erişim testi"""
        self.client.force_authenticate(user=None)
        url = reverse('dashboard-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_permission_denied(self):
        """İzin reddedilme testi"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('dashboard-detail', args=[self.dashboard.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_rate_limiting(self):
        """Rate limiting testi"""
        url = reverse('dashboardwidget-refresh', args=[self.widget.id])
        
        # Rate limit'i aşana kadar istek gönder
        for _ in range(301):  # Limit 300/saat
            response = self.client.post(url)
            
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
