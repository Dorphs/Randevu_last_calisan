from django.test import TestCase, LiveServerTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ...models.reports import Dashboard, DashboardWidget
from ...models.meetings import Meeting
from django.utils import timezone
from datetime import timedelta
import json
import time

User = get_user_model()

class DashboardFlowTest(TestCase):
    """Dashboard akış testleri - API entegrasyonu"""
    
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
    
    def test_complete_dashboard_flow(self):
        """Tam dashboard akışı testi"""
        
        # 1. Dashboard oluştur
        dashboard_data = {
            'title': 'Test Dashboard',
            'description': 'Integration Test Dashboard',
            'is_public': False
        }
        
        response = self.client.post(
            reverse('dashboard-list'),
            dashboard_data,
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        dashboard_id = response.data['id']
        
        # 2. Widget ekle
        widget_data = {
            'dashboard': dashboard_id,
            'title': 'Meeting Trend',
            'widget_type': 'MEETING_TREND',
            'position': {'x': 0, 'y': 0, 'w': 6, 'h': 4}
        }
        
        response = self.client.post(
            reverse('dashboardwidget-list'),
            widget_data,
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        widget_id = response.data['id']
        
        # 3. Widget verilerini yenile
        response = self.client.post(
            reverse('dashboardwidget-refresh', args=[widget_id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        
        # 4. Widget pozisyonunu güncelle
        position_data = {
            'x': 1,
            'y': 1,
            'w': 4,
            'h': 3
        }
        
        response = self.client.put(
            reverse('dashboardwidget-position', args=[widget_id]),
            position_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        
        # 5. Dashboard'u dışa aktar
        response = self.client.post(
            reverse('dashboard-export', args=[dashboard_id]) + '?format=excel'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('file_url', response.data)
        
        # 6. Dashboard'u paylaş
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        
        share_data = {
            'user_ids': [other_user.id]
        }
        
        response = self.client.post(
            reverse('dashboard-share', args=[dashboard_id]),
            share_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        
        # 7. Paylaşılan kullanıcı olarak eriş
        other_client = APIClient()
        other_client.force_authenticate(user=other_user)
        
        response = other_client.get(
            reverse('dashboard-detail', args=[dashboard_id])
        )
        self.assertEqual(response.status_code, 200)

class DashboardUITest(LiveServerTestCase):
    """Dashboard UI entegrasyon testleri"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        cls.selenium = webdriver.Chrome(options=options)
        cls.selenium.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
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
    
    def test_dashboard_ui_flow(self):
        """UI akış testi"""
        
        # Login
        self.selenium.get(f'{self.live_server_url}/login/')
        username_input = self.selenium.find_element(By.NAME, 'username')
        password_input = self.selenium.find_element(By.NAME, 'password')
        
        username_input.send_keys('testuser')
        password_input.send_keys('testpass123')
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Dashboard sayfasına git
        self.selenium.get(f'{self.live_server_url}/dashboards/{self.dashboard.id}/')
        
        # Widget'ın görünür olmasını bekle
        widget_element = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, f'widget-{self.widget.id}'))
        )
        self.assertTrue(widget_element.is_displayed())
        
        # Widget'ı yenile
        refresh_button = self.selenium.find_element(
            By.CSS_SELECTOR,
            f'#widget-{self.widget.id} .widget-actions button'
        )
        refresh_button.click()
        
        # Export menüsünü aç
        export_button = self.selenium.find_element(
            By.CSS_SELECTOR,
            '.dashboard-actions .dropdown-toggle'
        )
        export_button.click()
        
        # Excel export'u seç
        excel_export = self.selenium.find_element(
            By.CSS_SELECTOR,
            'a[onclick*="exportDashboard(\'excel\')"]'
        )
        excel_export.click()
        
        # Widget ekleme modalını aç
        add_widget_button = self.selenium.find_element(
            By.CSS_SELECTOR,
            '.add-widget-btn'
        )
        add_widget_button.click()
        
        # Modal'ın açılmasını bekle
        modal = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'addWidgetModal'))
        )
        self.assertTrue(modal.is_displayed())
