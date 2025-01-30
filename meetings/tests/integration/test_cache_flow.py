from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from ...models.reports import Dashboard, DashboardWidget
from ...models.meetings import Meeting
from ...services.dashboard_service import DashboardService
from ...services.cache_service import CacheService
import time

User = get_user_model()

class CacheFlowTest(TestCase):
    """Cache akış testleri"""
    
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
            refresh_interval=300  # 5 dakika
        )
        
        # Test verileri oluştur
        self.create_test_data()
        
    def tearDown(self):
        cache.clear()
        
    def create_test_data(self):
        """Test verilerini oluştur"""
        now = timezone.now()
        
        for i in range(10):
            Meeting.objects.create(
                title=f'Meeting {i}',
                start_time=now - timedelta(days=i),
                end_time=now - timedelta(days=i) + timedelta(hours=1),
                status=Meeting.StatusTypes.COMPLETED,
                organizer=self.user
            )
    
    def test_widget_cache_flow(self):
        """Widget cache akış testi"""
        
        # 1. İlk veri yüklemesi - cache yok
        start_time = time.time()
        data1 = DashboardService.refresh_widget(self.widget)
        first_load_time = time.time() - start_time
        
        # Cache key'i kontrol et
        cache_key = CacheService.get_cache_key(
            'widget_data',
            self.widget.id,
            {'type': self.widget.widget_type}
        )
        cached_data = cache.get(cache_key)
        self.assertEqual(cached_data, data1)
        
        # 2. İkinci yükleme - cache'den gelmeli
        start_time = time.time()
        data2 = DashboardService.refresh_widget(self.widget)
        cached_load_time = time.time() - start_time
        
        # Cache'den gelen veri aynı olmalı
        self.assertEqual(data1, data2)
        
        # Cache'den yükleme daha hızlı olmalı
        self.assertLess(cached_load_time, first_load_time)
        
        # 3. Cache invalidation
        Meeting.objects.create(
            title='New Meeting',
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
            status=Meeting.StatusTypes.COMPLETED,
            organizer=self.user
        )
        
        CacheService.invalidate_widget_cache(self.widget.id)
        
        # Cache temizlenmeli
        cached_data = cache.get(cache_key)
        self.assertIsNone(cached_data)
        
        # 4. Yeni veri yüklemesi
        data3 = DashboardService.refresh_widget(self.widget)
        self.assertNotEqual(data2, data3)
    
    def test_dashboard_cache_flow(self):
        """Dashboard cache akış testi"""
        
        # 1. Dashboard verilerini cache'le
        dashboard_data = {
            'widgets': [
                DashboardService.refresh_widget(self.widget)
            ]
        }
        
        cache_key = CacheService.get_cache_key(
            'dashboard_data',
            self.dashboard.id
        )
        
        CacheService.cache_dashboard_data(self.dashboard.id, dashboard_data)
        
        # 2. Cache'den veriyi al
        cached_data = CacheService.get_cached_dashboard_data(self.dashboard.id)
        self.assertEqual(dashboard_data, cached_data)
        
        # 3. Widget güncelleme
        new_position = {'x': 1, 'y': 1, 'w': 4, 'h': 3}
        DashboardService.update_widget_position(self.widget, new_position)
        
        # Dashboard cache'i temizlenmeli
        cached_data = cache.get(cache_key)
        self.assertIsNone(cached_data)
    
    def test_cache_timeout_flow(self):
        """Cache timeout akış testi"""
        
        # 1. Kısa süreli cache
        short_cache_key = CacheService.get_cache_key(
            'short_test',
            'test_data'
        )
        
        cache.set(short_cache_key, 'test_value', timeout=1)
        
        # Veri cache'de olmalı
        self.assertEqual(cache.get(short_cache_key), 'test_value')
        
        # Cache süresinin dolmasını bekle
        time.sleep(2)
        
        # Veri cache'den silinmeli
        self.assertIsNone(cache.get(short_cache_key))
        
        # 2. Widget refresh interval kontrolü
        data1 = DashboardService.refresh_widget(self.widget)
        
        # Refresh interval'dan önce aynı veri gelmeli
        time.sleep(1)
        data2 = DashboardService.refresh_widget(self.widget)
        self.assertEqual(data1, data2)
        
    def test_cache_race_condition_flow(self):
        """Cache race condition akış testi"""
        
        # 1. Parallel widget yenileme simülasyonu
        def refresh_widget():
            return DashboardService.refresh_widget(self.widget)
        
        # İlk yenileme
        data1 = refresh_widget()
        
        # Cache'i temizle
        CacheService.invalidate_widget_cache(self.widget.id)
        
        # Parallel yenilemeler
        data2 = refresh_widget()
        data3 = refresh_widget()
        
        # Tüm veriler tutarlı olmalı
        self.assertEqual(data2, data3)
