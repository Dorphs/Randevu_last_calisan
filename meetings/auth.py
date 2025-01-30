from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import BasePermission
from django.core.cache import cache
from django.conf import settings
import time

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Rate limiting kontrolü
        ip = self.get_client_ip(request)
        if not self.check_rate_limit(ip):
            return None
        
        return super().authenticate(request)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def check_rate_limit(self, ip):
        cache_key = f'rate_limit_{ip}'
        requests = cache.get(cache_key, [])
        now = time.time()
        
        # Son 1 dakikadaki istekleri filtrele
        requests = [req for req in requests if now - req < 60]
        
        if len(requests) >= settings.RATE_LIMIT_PER_MINUTE:
            return False
        
        requests.append(now)
        cache.set(cache_key, requests, 60)
        return True

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class IsMeetingParticipant(BasePermission):
    """
    Toplantı katılımcısı veya organizatörü için izin kontrolü
    """
    def has_object_permission(self, request, view, obj):
        # Admin her şeyi yapabilir
        if request.user.is_staff:
            return True
        
        # Toplantının organizatörü veya katılımcısı mı?
        return (obj.visitor.user == request.user or 
                obj.participants.filter(user=request.user).exists())
