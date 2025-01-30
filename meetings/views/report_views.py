from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from ..models.reports import Report, ReportExecution, Dashboard, DashboardWidget
from ..services.report_service import ReportService
from ..serializers.report_serializers import (
    ReportSerializer, 
    ReportExecutionSerializer,
    DashboardSerializer, 
    DashboardWidgetSerializer
)

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Rapor oluşturur"""
        report = self.get_object()
        
        # Rapor parametrelerini al
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        parameters = request.data.get('parameters', {})

        # Rapor tipine göre servis metodunu çağır
        if report.report_type == Report.ReportTypes.MEETING_SUMMARY:
            data = ReportService.generate_meeting_summary(start_date, end_date, parameters)
        elif report.report_type == Report.ReportTypes.VISITOR_ANALYTICS:
            data = ReportService.generate_visitor_analytics(start_date, end_date, parameters)
        elif report.report_type == Report.ReportTypes.ROOM_USAGE:
            data = ReportService.generate_room_usage(start_date, end_date, parameters)
        elif report.report_type == Report.ReportTypes.ATTENDANCE:
            data = ReportService.generate_attendance_report(start_date, end_date, parameters)
        else:
            return Response(
                {"error": "Geçersiz rapor tipi"},
                status=status.HTTP_400_BAD_REQUEST
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

    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """Raporu Excel formatında export eder"""
        report = self.get_object()
        execution_id = request.data.get('execution_id')
        
        try:
            execution = ReportExecution.objects.get(id=execution_id)
            file_path = ReportService.export_to_excel(
                execution.result_file.read(),
                report.report_type
            )
            return Response({
                'file_url': file_path
            })
        except ReportExecution.DoesNotExist:
            return Response(
                {"error": "Rapor çalıştırma kaydı bulunamadı"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Rapor zamanlaması yapar"""
        report = self.get_object()
        frequency = request.data.get('frequency')
        
        if frequency not in ['daily', 'weekly', 'monthly']:
            return Response(
                {"error": "Geçersiz zamanlama sıklığı"},
                status=status.HTTP_400_BAD_REQUEST
            )

        ReportService.schedule_report(report.id, frequency)
        return Response({
            "message": "Rapor zamanlaması oluşturuldu"
        })

class DashboardViewSet(viewsets.ModelViewSet):
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Kullanıcıya özel dashboard'ları filtrele"""
        return Dashboard.objects.filter(
            Q(owner=self.request.user) |
            Q(shared_with=self.request.user) |
            Q(is_public=True)
        ).distinct()

    @action(detail=True, methods=['post'])
    def add_widget(self, request, pk=None):
        """Dashboard'a widget ekler"""
        dashboard = self.get_object()
        widget_data = request.data
        
        widget = ReportService.create_dashboard_widget(dashboard.id, widget_data)
        serializer = DashboardWidgetSerializer(widget)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Dashboard'ı diğer kullanıcılarla paylaşır"""
        dashboard = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        dashboard.shared_with.add(*user_ids)
        return Response({
            "message": "Dashboard paylaşıldı"
        })

    @action(detail=True, methods=['post'])
    def update_layout(self, request, pk=None):
        """Dashboard widget yerleşimini günceller"""
        dashboard = self.get_object()
        layout = request.data.get('layout', {})
        
        dashboard.layout = layout
        dashboard.save()
        return Response({
            "message": "Dashboard yerleşimi güncellendi"
        })
