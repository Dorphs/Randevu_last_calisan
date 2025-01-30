from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models.reports import Dashboard, DashboardWidget
from ..serializers.dashboard_serializers import (
    DashboardSerializer,
    DashboardWidgetSerializer,
    WidgetPositionSerializer
)
from ..services.dashboard_service import DashboardService
from ..permissions import IsOwnerOrSharedWith
from ..throttling import DashboardThrottle, WidgetThrottle

class DashboardViewSet(viewsets.ModelViewSet):
    serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrSharedWith]
    throttle_classes = [DashboardThrottle]
    
    def get_queryset(self):
        user = self.request.user
        return Dashboard.objects.filter(
            owner=user
        ) | Dashboard.objects.filter(
            shared_with=user
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Dashboard'u diğer kullanıcılarla paylaş"""
        dashboard = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        try:
            DashboardService.share_dashboard(dashboard, user_ids)
            return Response({'status': 'Dashboard paylaşıldı'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """Dashboard verilerini dışa aktar"""
        dashboard = self.get_object()
        format = request.query_params.get('format', 'excel')
        
        try:
            file_url = DashboardService.export_dashboard(dashboard, format)
            return Response({'file_url': file_url})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class DashboardWidgetViewSet(viewsets.ModelViewSet):
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [WidgetThrottle]
    
    def get_queryset(self):
        return DashboardWidget.objects.filter(
            dashboard__owner=self.request.user
        ) | DashboardWidget.objects.filter(
            dashboard__shared_with=self.request.user
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """Widget verilerini yenile"""
        widget = self.get_object()
        
        try:
            data = DashboardService.refresh_widget(widget)
            return Response(data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['put'])
    def position(self, request, pk=None):
        """Widget pozisyonunu güncelle"""
        widget = self.get_object()
        serializer = WidgetPositionSerializer(data=request.data)
        
        if serializer.is_valid():
            DashboardService.update_widget_position(
                widget,
                serializer.validated_data
            )
            return Response({'status': 'Pozisyon güncellendi'})
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """Widget verilerini dışa aktar"""
        widget = self.get_object()
        format = request.query_params.get('format', 'excel')
        
        try:
            file_url = DashboardService.export_widget(widget, format)
            return Response({'file_url': file_url})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
