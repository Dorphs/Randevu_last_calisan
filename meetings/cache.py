from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib
import json

class CacheService:
    @staticmethod
    def get_cache_key(prefix, *args, **kwargs):
        """Cache anahtarı oluşturur"""
        key_parts = [prefix]
        
        # Args'ları ekle
        for arg in args:
            if isinstance(arg, (dict, list)):
                key_parts.append(hashlib.md5(
                    json.dumps(arg, sort_keys=True).encode()
                ).hexdigest())
            else:
                key_parts.append(str(arg))
        
        # Kwargs'ları ekle
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            kwargs_str = hashlib.md5(
                json.dumps(sorted_kwargs).encode()
            ).hexdigest()
            key_parts.append(kwargs_str)
        
        return ':'.join(key_parts)

    @staticmethod
    def cache_response(timeout=300):
        """View response'larını cache'ler"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Cache key oluştur
                cache_key = CacheService.get_cache_key(
                    func.__name__,
                    *args,
                    **kwargs
                )
                
                # Cache'den veriyi al
                cached_response = cache.get(cache_key)
                if cached_response is not None:
                    return cached_response
                
                # Fonksiyonu çalıştır ve sonucu cache'le
                response = func(*args, **kwargs)
                cache.set(cache_key, response, timeout)
                return response
            return wrapper
        return decorator

    @staticmethod
    def cache_queryset(timeout=300):
        """QuerySet sonuçlarını cache'ler"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Cache key oluştur
                cache_key = CacheService.get_cache_key(
                    func.__name__,
                    *args,
                    **kwargs
                )
                
                # Cache'den veriyi al
                cached_data = cache.get(cache_key)
                if cached_data is not None:
                    return cached_data
                
                # QuerySet'i çalıştır ve sonucu cache'le
                queryset = func(*args, **kwargs)
                cache.set(cache_key, list(queryset), timeout)
                return queryset
            return wrapper
        return decorator

def cache_dashboard_data(dashboard_id, data, timeout=300):
    """Dashboard verilerini cache'ler"""
    cache_key = f'dashboard:{dashboard_id}:data'
    cache.set(cache_key, data, timeout)

def get_cached_dashboard_data(dashboard_id):
    """Cache'lenmiş dashboard verilerini getirir"""
    cache_key = f'dashboard:{dashboard_id}:data'
    return cache.get(cache_key)

def cache_widget_data(widget_id, data, timeout=300):
    """Widget verilerini cache'ler"""
    cache_key = f'widget:{widget_id}:data'
    cache.set(cache_key, data, timeout)

def get_cached_widget_data(widget_id):
    """Cache'lenmiş widget verilerini getirir"""
    cache_key = f'widget:{widget_id}:data'
    return cache.get(cache_key)

def invalidate_dashboard_cache(dashboard_id):
    """Dashboard cache'ini temizler"""
    cache_key = f'dashboard:{dashboard_id}:data'
    cache.delete(cache_key)

def invalidate_widget_cache(widget_id):
    """Widget cache'ini temizler"""
    cache_key = f'widget:{widget_id}:data'
    cache.delete(cache_key)
