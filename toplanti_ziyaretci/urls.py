"""
URL configuration for toplanti_ziyaretci project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import views

# API router'ını oluştur
router = DefaultRouter()
router.register(r'users', views.UserViewSet)  # Kullanıcı API'si
router.register(r'toplanti-odalari', views.ToplantiOdasiViewSet)  # Toplantı odası API'si
router.register(r'toplantilar', views.ToplantiViewSet)  # Toplantı API'si
router.register(r'ziyaretciler', views.ZiyaretciViewSet)  # Ziyaretçi API'si

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin paneli
    path('api/', include(router.urls)),  # API endpoint'leri
    path('api/login/', views.login_view, name='login'),  # Login endpoint'i
    path('api/raporlar/ziyaretci/', views.ziyaretci_raporlari, name='ziyaretci-raporlari'),  # Ziyaretçi raporları
    path('api/raporlar/toplanti/', views.toplanti_raporlari, name='toplanti-raporlari'),  # Toplantı raporları
    path('api/raporlar/mevcut-tarihler/', views.mevcut_tarihler, name='mevcut_tarihler'),  # Mevcut tarihler
]
