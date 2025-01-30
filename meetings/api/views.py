from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

from ..models.reports import Report, ReportExecution, Dashboard, DashboardWidget
from ..serializers.report_serializers import (
    ReportSerializer,
    ReportExecutionSerializer,
    DashboardSerializer,
    DashboardWidgetSerializer
)
from ..services.report_service import ReportService
from ..cache import (
    CacheService,
    cache_dashboard_data,
    get_cached_dashboard_data,
    cache_widget_data,
    get_cached_widget_data,
    invalidate_dashboard_cache,
    invalidate_widget_cache
)
from .throttling import (
    ReportGenerationThrottle,
    DashboardRefreshThrottle,
    ExportThrottle,
    WidgetRefreshThrottle
)
from .permissions import (
    IsReportOwnerOrRecipient,
    IsDashboardOwnerOrShared,
    IsWidgetDashboardOwnerOrShared
)

class ReportExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReportExecutionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Kullanıcıya özel rapor çalıştırmalarını filtrele"""
        user_reports = Report.objects.filter(
            Q(created_by=self.request.user) |
            Q(recipients=self.request.user)
        )
        return ReportExecution.objects.filter(report__in=user_reports)

class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Kullanıcıya özel raporları filtrele"""
        return Report.objects.filter(
            Q(created_by=self.request.user) |
            Q(recipients=self.request.user)
        )

    def perform_create(self, serializer):
        """Rapor oluştururken mevcut kullanıcıyı ekle"""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    @CacheService.cache_response(timeout=300)
    def generate(self, request, pk=None):
        """Rapor oluştur"""
        report = self.get_object()
        throttle_classes = [ReportGenerationThrottle]
        permission_classes = [IsReportOwnerOrRecipient]

        # Eğer rapor zaten oluşturuluyorsa, bekleyin
        if cache.get(f'report_generation_{report.id}'):
            return Response(
                {"error": "Rapor zaten oluşturuluyor"},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        try:
            # Cache kilidi oluştur
            cache.set(f'report_generation_{report.id}', True, timeout=300)  # 5 dakika timeout

            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            parameters = request.data.get('parameters', {})

            # Rapor verilerini oluştur
            data = ReportService.generate_report_data(
                report.report_type,
                start_date,
                end_date,
                parameters
            )

            # Rapor çalıştırma kaydı oluştur
            execution = ReportExecution.objects.create(
                report=report,
                status=ReportExecution.StatusTypes.COMPLETED,
                start_time=timezone.now(),
                end_time=timezone.now(),
                execution_parameters={
                    'start_date': start_date,
                    'end_date': end_date,
                    'parameters': parameters
                }
            )

            return Response({
                'execution_id': execution.id,
                'data': data
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        finally:
            # Cache kilidini kaldır
            cache.delete(f'report_generation_{report.id}')

    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """Raporu dışa aktar"""
        report = self.get_object()
        execution_id = request.data.get('execution_id')
        export_format = request.data.get('format', 'excel')
        throttle_classes = [ExportThrottle]
        permission_classes = [IsReportOwnerOrRecipient]

        try:
            execution = ReportExecution.objects.get(id=execution_id)
            if export_format == 'excel':
                file_path = ReportService.export_to_excel(
                    execution.result_file.read(),
                    report.report_type
                )
            elif export_format == 'pdf':
                file_path = ReportService.export_to_pdf(
                    execution.result_file.read(),
                    report.report_type
                )
            else:
                return Response(
                    {"error": "Desteklenmeyen format"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({
                'file_url': file_path
            })
        except ReportExecution.DoesNotExist:
            return Response(
                {"error": "Rapor çalıştırma kaydı bulunamadı"},
                status=status.HTTP_404_NOT_FOUND
            )

class DashboardViewSet(viewsets.ModelViewSet):
    serializer_class = DashboardSerializer
    permission_classes = [permissions.IsAuthenticated, IsDashboardOwnerOrShared]
    throttle_classes = [DashboardRefreshThrottle]

    def get_queryset(self):
        """Kullanıcıya özel dashboard'ları filtrele"""
        return Dashboard.objects.filter(
            Q(owner=self.request.user) |
            Q(shared_with=self.request.user) |
            Q(is_public=True)
        ).distinct()

    def perform_create(self, serializer):
        """Dashboard oluştururken mevcut kullanıcıyı ekle"""
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def add_widget(self, request, pk=None):
        """Dashboard'a widget ekle"""
        dashboard = self.get_object()
        widget_data = request.data

        # Widget oluştur
        widget = ReportService.create_dashboard_widget(
            dashboard.id,
            widget_data
        )
        serializer = DashboardWidgetSerializer(widget)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Dashboard'ı paylaş"""
        dashboard = self.get_object()
        user_ids = request.data.get('user_ids', [])

        dashboard.shared_with.add(*user_ids)
        return Response({
            "message": "Dashboard başarıyla paylaşıldı"
        })

class DashboardWidgetViewSet(viewsets.ModelViewSet):
    serializer_class = DashboardWidgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsWidgetDashboardOwnerOrShared]
    throttle_classes = [WidgetRefreshThrottle]

    def get_queryset(self):
        """Kullanıcının erişimi olan widget'ları filtrele"""
        accessible_dashboards = Dashboard.objects.filter(
            Q(owner=self.request.user) |
            Q(shared_with=self.request.user) |
            Q(is_public=True)
        )
        return DashboardWidget.objects.filter(
            dashboard__in=accessible_dashboards
        )

    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """Widget verilerini yenile"""
        widget = self.get_object()
        
        try:
            # Widget verilerini güncelle
            if widget.widget_type == DashboardWidget.WidgetTypes.CHART:
                data = ReportService.update_chart_widget(widget.id)
            elif widget.widget_type == DashboardWidget.WidgetTypes.TABLE:
                data = ReportService.update_table_widget(widget.id)
            elif widget.widget_type == DashboardWidget.WidgetTypes.METRIC:
                data = ReportService.update_metric_widget(widget.id)
            else:
                return Response(
                    {"error": "Desteklenmeyen widget tipi"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(data)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
