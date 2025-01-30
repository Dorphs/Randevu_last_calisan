from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReportViewSet,
    DashboardViewSet,
    ReportExecutionViewSet,
    DashboardWidgetViewSet
)

router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'dashboards', DashboardViewSet, basename='dashboard')
router.register(r'report-executions', ReportExecutionViewSet, basename='report-execution')
router.register(r'dashboard-widgets', DashboardWidgetViewSet, basename='dashboard-widget')

urlpatterns = [
    path('', include(router.urls)),
    
    # Özel rapor endpoint'leri
    path('reports/<int:pk>/generate/', 
         ReportViewSet.as_view({'post': 'generate'}),
         name='report-generate'),
    path('reports/<int:pk>/export/', 
         ReportViewSet.as_view({'post': 'export'}),
         name='report-export'),
    path('reports/<int:pk>/schedule/', 
         ReportViewSet.as_view({'post': 'schedule'}),
         name='report-schedule'),
    
    # Dashboard endpoint'leri
    path('dashboards/<int:pk>/add-widget/',
         DashboardViewSet.as_view({'post': 'add_widget'}),
         name='dashboard-add-widget'),
    path('dashboards/<int:pk>/share/',
         DashboardViewSet.as_view({'post': 'share'}),
         name='dashboard-share'),
    path('dashboards/<int:pk>/update-layout/',
         DashboardViewSet.as_view({'post': 'update_layout'}),
         name='dashboard-update-layout'),
    
    # Widget endpoint'leri
    path('widgets/<int:pk>/refresh/',
         DashboardWidgetViewSet.as_view({'post': 'refresh'}),
         name='widget-refresh'),
]
