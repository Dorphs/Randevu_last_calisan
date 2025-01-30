from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Toplantı Yönetim Sistemi API",
        default_version='v1',
        description="""
        Toplantı Yönetim Sistemi için REST API dokümantasyonu.
        
        ## Özellikler
        
        * 👥 Kullanıcı Yönetimi
        * 📅 Toplantı Yönetimi
        * 🏢 Ziyaretçi Yönetimi
        * 📊 Raporlama ve Dashboard
        
        ## Kimlik Doğrulama
        
        API JWT token tabanlı kimlik doğrulama kullanmaktadır. Token almak için:
        
        ```
        POST /api/token/
        {
            "username": "your_username",
            "password": "your_password"
        }
        ```
        
        ## Rate Limiting
        
        * Rapor Oluşturma: 10/saat
        * Dashboard Yenileme: 30/dakika
        * Export İşlemleri: 20/saat
        * Widget Yenileme: 60/dakika
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.IsAuthenticated],
)
