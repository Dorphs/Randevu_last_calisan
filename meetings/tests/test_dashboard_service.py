from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from ..models.reports import Dashboard, DashboardWidget
from ..models.meetings import Meeting
from ..services.dashboard_service import DashboardService
from django.core.cache import cache

User = get_user_model()

class DashboardServiceTests(TestCase):
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
            widget_type='MEETING_TREND'
        )
        
        # Test toplantıları oluştur
        now = timezone.now()
        
        # Son 30 gün için toplantılar
        for i in range(30):
            Meeting.objects.create(
                title=f'Meeting {i}',
                start_time=now - timedelta(days=i),
                end_time=now - timedelta(days=i) + timedelta(hours=1),
                status=Meeting.StatusTypes.COMPLETED,
                organizer=self.user
            )
            
        # İptal edilen toplantılar
        for i in range(5):
            Meeting.objects.create(
                title=f'Cancelled Meeting {i}',
                start_time=now - timedelta(days=i),
                end_time=now - timedelta(days=i) + timedelta(hours=1),
                status=Meeting.StatusTypes.CANCELLED,
                organizer=self.user
            )
            
        # Planlanan toplantılar
        for i in range(3):
            Meeting.objects.create(
                title=f'Planned Meeting {i}',
                start_time=now + timedelta(days=i),
                end_time=now + timedelta(days=i) + timedelta(hours=1),
                status=Meeting.StatusTypes.PLANNED,
                organizer=self.user
            )
    
    def tearDown(self):
        cache.clear()
    
    def test_get_meeting_trend_data(self):
        """Toplantı trendi verisi testi"""
        data = DashboardService.get_meeting_trend_data()
        
        self.assertIn('labels', data)
        self.assertIn('meetings', data)
        self.assertEqual(len(data['labels']), len(data['meetings']))
        self.assertTrue(all(isinstance(x, int) for x in data['meetings']))
        
    def test_get_meeting_status_data(self):
        """Toplantı durumları verisi testi"""
        data = DashboardService.get_meeting_status_data()
        
        self.assertEqual(data['completed'], 30)
        self.assertEqual(data['cancelled'], 5)
        self.assertEqual(data['planned'], 3)
        
    def test_get_meeting_duration_data(self):
        """Toplantı süreleri verisi testi"""
        data = DashboardService.get_meeting_duration_data()
        
        self.assertIn('labels', data)
        self.assertIn('durations', data)
        self.assertEqual(len(data['labels']), len(data['durations']))
        
    def test_refresh_widget(self):
        """Widget yenileme testi"""
        # İlk çağrı - cache'den değil
        data1 = DashboardService.refresh_widget(self.widget)
        self.assertIsNotNone(data1)
        
        # İkinci çağrı - cache'den gelmeli
        data2 = DashboardService.refresh_widget(self.widget)
        self.assertEqual(data1, data2)
        
    def test_update_widget_position(self):
        """Widget pozisyon güncelleme testi"""
        new_position = {'x': 1, 'y': 1, 'w': 4, 'h': 3}
        DashboardService.update_widget_position(self.widget, new_position)
        
        self.widget.refresh_from_db()
        self.assertEqual(self.widget.position, new_position)
        
    def test_share_dashboard(self):
        """Dashboard paylaşım testi"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        
        DashboardService.share_dashboard(self.dashboard, [other_user.id])
        self.assertIn(other_user, self.dashboard.shared_with.all())
        
    def test_export_dashboard(self):
        """Dashboard dışa aktarma testi"""
        # Excel formatı
        excel_url = DashboardService.export_dashboard(self.dashboard, 'excel')
        self.assertTrue(excel_url.endswith('.xlsx'))
        
        # PDF formatı
        pdf_url = DashboardService.export_dashboard(self.dashboard, 'pdf')
        self.assertTrue(pdf_url.endswith('.pdf'))
        
    def test_export_widget(self):
        """Widget dışa aktarma testi"""
        # Excel formatı
        excel_url = DashboardService.export_widget(self.widget, 'excel')
        self.assertTrue(excel_url.endswith('.xlsx'))
        
        # PDF formatı
        pdf_url = DashboardService.export_widget(self.widget, 'pdf')
        self.assertTrue(pdf_url.endswith('.pdf'))
        
    def test_invalid_widget_type(self):
        """Geçersiz widget tipi testi"""
        invalid_widget = DashboardWidget.objects.create(
            dashboard=self.dashboard,
            title='Invalid Widget',
            widget_type='INVALID_TYPE'
        )
        
        data = DashboardService.refresh_widget(invalid_widget)
        self.assertEqual(data, {})
