from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class ReportGenerationThrottle(UserRateThrottle):
    """Rapor oluşturma için rate limiting"""
    rate = '10/hour'  # Saatte 10 rapor
    scope = 'report_generation'

class DashboardRefreshThrottle(UserRateThrottle):
    """Dashboard yenileme için rate limiting"""
    rate = '30/minute'  # Dakikada 30 yenileme
    scope = 'dashboard_refresh'

class DashboardThrottle(UserRateThrottle):
    rate = '100/hour'
    scope = 'dashboard'

class WidgetRefreshThrottle(UserRateThrottle):
    """Widget yenileme için rate limiting"""
    rate = '60/minute'  # Dakikada 60 yenileme
    scope = 'widget_refresh'

class WidgetThrottle(UserRateThrottle):
    rate = '300/hour'  # Widget'lar daha sık yenilenebilir
    scope = 'widget'

class ExportThrottle(UserRateThrottle):
    rate = '20/hour'  # Export işlemleri için daha sıkı limit
    scope = 'export'
