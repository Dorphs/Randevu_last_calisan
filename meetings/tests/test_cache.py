from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth import get_user_model
from ..models.reports import Dashboard, DashboardWidget
from ..cache import (
    CacheService,
    cache_dashboard_data,
    get_cached_dashboard_data,
    cache_widget_data,
    get_cached_widget_data,
    invalidate_dashboard_cache,
    invalidate_widget_cache
)

User = get_user_model()

class CacheTests(TestCase):
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
            widget_type=DashboardWidget.WidgetTypes.CHART
        )
        
    def tearDown(self):
        # Her test sonrası cache'i temizle
        cache.clear()
        
    def test_cache_key_generation(self):
        """Cache anahtarı oluşturma testi"""
        key = CacheService.get_cache_key(
            'test',
            123,
            {'a': 1, 'b': 2}
        )
        self.assertTrue(isinstance(key, str))
        self.assertTrue(key.startswith('test:'))
        
    def test_dashboard_cache(self):
        """Dashboard cache testi"""
        test_data = {'key': 'value'}
        
        # Veriyi cache'e kaydet
        cache_dashboard_data(self.dashboard.id, test_data)
        
        # Cache'den veriyi al
        cached_data = get_cached_dashboard_data(self.dashboard.id)
        self.assertEqual(cached_data, test_data)
        
        # Cache'i temizle
        invalidate_dashboard_cache(self.dashboard.id)
        
        # Cache'in temizlendiğini kontrol et
        cleared_data = get_cached_dashboard_data(self.dashboard.id)
        self.assertIsNone(cleared_data)
        
    def test_widget_cache(self):
        """Widget cache testi"""
        test_data = {'type': 'chart', 'data': [1, 2, 3]}
        
        # Veriyi cache'e kaydet
        cache_widget_data(self.widget.id, test_data)
        
        # Cache'den veriyi al
        cached_data = get_cached_widget_data(self.widget.id)
        self.assertEqual(cached_data, test_data)
        
        # Cache'i temizle
        invalidate_widget_cache(self.widget.id)
        
        # Cache'in temizlendiğini kontrol et
        cleared_data = get_cached_widget_data(self.widget.id)
        self.assertIsNone(cleared_data)
        
    def test_cache_response_decorator(self):
        """Cache response decorator testi"""
        @CacheService.cache_response(timeout=300)
        def test_function(param):
            return {'result': param}
        
        # İlk çağrı
        result1 = test_function('test')
        
        # İkinci çağrı (cache'den gelmeli)
        result2 = test_function('test')
        
        self.assertEqual(result1, result2)
        
    def test_cache_queryset_decorator(self):
        """Cache queryset decorator testi"""
        @CacheService.cache_queryset(timeout=300)
        def test_queryset():
            return Dashboard.objects.all()
        
        # İlk çağrı
        result1 = list(test_queryset())
        
        # Yeni dashboard ekle
        Dashboard.objects.create(
            title='New Dashboard',
            owner=self.user
        )
        
        # İkinci çağrı (cache'den gelmeli, yeni dashboard görünmemeli)
        result2 = list(test_queryset())
        
        self.assertEqual(len(result1), len(result2))
