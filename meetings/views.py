from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth, TruncWeek
from django_filters.rest_framework import DjangoFilterBackend
from .models import Visitor, Meeting, MeetingRoom, MeetingNote
from .serializers import (
    VisitorSerializer, MeetingSerializer, 
    MeetingRoomSerializer, MeetingNoteSerializer
)
from .exceptions import (
    MeetingConflictError, RoomNotAvailableError, 
    InvalidMeetingTimeError, InvalidMeetingStatusTransition
)
import django_filters
import logging
from django.http import HttpResponse
from .resources import VisitorResource, MeetingResource
from .reports import create_meeting_report_pdf, create_visitor_report_pdf
import csv
from datetime import datetime

logger = logging.getLogger(__name__)

class VisitorFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    company = django_filters.CharFilter(lookup_expr='icontains')
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Visitor
        fields = ['name', 'company', 'created_at']

class MeetingFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    visitor = django_filters.ModelChoiceFilter(queryset=Visitor.objects.all())
    start_time = django_filters.DateTimeFromToRangeFilter()
    status = django_filters.ChoiceFilter(choices=Meeting.STATUS_CHOICES)
    meeting_type = django_filters.ChoiceFilter(choices=Meeting.MEETING_TYPES)
    priority = django_filters.ChoiceFilter(choices=Meeting.PRIORITY_CHOICES)

    class Meta:
        model = Meeting
        fields = ['title', 'visitor', 'start_time', 'status', 'meeting_type', 'priority']

class VisitorViewSet(viewsets.ModelViewSet):
    queryset = Visitor.objects.all()
    serializer_class = VisitorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = VisitorFilter
    search_fields = ['name', 'company', 'email']
    ordering_fields = ['name', 'company', 'created_at']

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        total_visitors = Visitor.objects.count()
        visitors_by_company = Visitor.objects.values('company').annotate(
            count=Count('id')
        ).order_by('-count')
        meetings_by_visitor = Visitor.objects.annotate(
            meeting_count=Count('meetings')
        ).values('name', 'meeting_count').order_by('-meeting_count')[:5]

        return Response({
            'total_visitors': total_visitors,
            'visitors_by_company': visitors_by_company,
            'top_visitors': meetings_by_visitor,
        })

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        try:
            visitors_data = request.data
            created_visitors = []
            
            for visitor_data in visitors_data:
                serializer = self.get_serializer(data=visitor_data)
                serializer.is_valid(raise_exception=True)
                visitor = serializer.save()
                created_visitors.append(visitor)
            
            response_serializer = self.get_serializer(created_visitors, many=True)
            return Response(response_serializer.data, status=201)
        
        except Exception as e:
            logger.error('Bulk visitor creation error', exc_info=True)
            raise

    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        try:
            resource = VisitorResource()
            dataset = resource.export()
            
            response = HttpResponse(
                dataset.xlsx,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="visitors.xlsx"'
            return response
        
        except Exception as e:
            logger.error('Visitor export error', exc_info=True)
            raise

    @action(detail=False, methods=['post'])
    def import_excel(self, request):
        try:
            resource = VisitorResource()
            dataset = resource.load(request.FILES['file'])
            result = resource.import_data(dataset, dry_run=True)
            
            if not result.has_errors():
                resource.import_data(dataset, dry_run=False)
                return Response({'status': 'success', 'imported_count': len(dataset)})
            else:
                return Response({'status': 'error', 'errors': result.row_errors()}, status=400)
        
        except Exception as e:
            logger.error('Visitor import error', exc_info=True)
            raise

    @action(detail=False, methods=['get'])
    def report_pdf(self, request):
        try:
            visitors = self.get_queryset()
            pdf = create_visitor_report_pdf(visitors)
            
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="visitors_report.pdf"'
            response.write(pdf)
            return response
        
        except Exception as e:
            logger.error('Visitor PDF report error', exc_info=True)
            raise

class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = MeetingFilter
    search_fields = ['title', 'description', 'visitor__name']
    ordering_fields = ['start_time', 'created_at', 'priority']

    @action(detail=False, methods=['get'])
    def today(self, request):
        today = timezone.now().date()
        meetings = Meeting.objects.filter(
            start_time__date=today
        ).order_by('start_time')
        serializer = self.get_serializer(meetings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        now = timezone.now()
        meetings = Meeting.objects.filter(
            start_time__gt=now
        ).order_by('start_time')[:5]
        serializer = self.get_serializer(meetings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        now = timezone.now()
        last_month = now - timezone.timedelta(days=30)

        # Toplantı türlerine göre dağılım
        meetings_by_type = Meeting.objects.values('meeting_type').annotate(
            count=Count('id')
        )

        # Aylık toplantı sayıları
        monthly_meetings = Meeting.objects.annotate(
            month=TruncMonth('start_time')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        # Haftalık toplantı sayıları
        weekly_meetings = Meeting.objects.filter(
            start_time__gte=last_month
        ).annotate(
            week=TruncWeek('start_time')
        ).values('week').annotate(
            count=Count('id')
        ).order_by('week')

        # Durum dağılımı
        status_distribution = Meeting.objects.values('status').annotate(
            count=Count('id')
        )

        return Response({
            'meetings_by_type': meetings_by_type,
            'monthly_meetings': monthly_meetings,
            'weekly_meetings': weekly_meetings,
            'status_distribution': status_distribution,
        })

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        try:
            meetings_data = request.data
            created_meetings = []
            
            for meeting_data in meetings_data:
                serializer = self.get_serializer(data=meeting_data)
                serializer.is_valid(raise_exception=True)
                
                # Toplantı zamanı ve oda müsaitlik kontrolü
                start_time = serializer.validated_data.get('start_time')
                end_time = serializer.validated_data.get('end_time')
                room = serializer.validated_data.get('location')
                
                if start_time >= end_time:
                    raise InvalidMeetingTimeError()
                
                conflicting_meetings = Meeting.objects.filter(
                    location=room,
                    start_time__lt=end_time,
                    end_time__gt=start_time
                ).exists()
                
                if conflicting_meetings:
                    raise MeetingConflictError()
                
                meeting = serializer.save()
                created_meetings.append(meeting)
            
            response_serializer = self.get_serializer(created_meetings, many=True)
            return Response(response_serializer.data, status=201)
        
        except Exception as e:
            logger.error('Bulk meeting creation error', exc_info=True)
            raise

    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        try:
            resource = MeetingResource()
            dataset = resource.export()
            
            response = HttpResponse(
                dataset.xlsx,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="meetings.xlsx"'
            return response
        
        except Exception as e:
            logger.error('Meeting export error', exc_info=True)
            raise

    @action(detail=False, methods=['post'])
    def import_excel(self, request):
        try:
            resource = MeetingResource()
            dataset = resource.load(request.FILES['file'])
            result = resource.import_data(dataset, dry_run=True)
            
            if not result.has_errors():
                resource.import_data(dataset, dry_run=False)
                return Response({'status': 'success', 'imported_count': len(dataset)})
            else:
                return Response({'status': 'error', 'errors': result.row_errors()}, status=400)
        
        except Exception as e:
            logger.error('Meeting import error', exc_info=True)
            raise

    @action(detail=False, methods=['get'])
    def report_pdf(self, request):
        try:
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            status = request.query_params.get('status')
            meeting_type = request.query_params.get('meeting_type')
            
            meetings = self.get_queryset()
            
            if start_date:
                meetings = meetings.filter(start_time__date__gte=start_date)
            if end_date:
                meetings = meetings.filter(end_time__date__lte=end_date)
            if status:
                meetings = meetings.filter(status=status)
            if meeting_type:
                meetings = meetings.filter(meeting_type=meeting_type)
            
            pdf = create_meeting_report_pdf(meetings)
            
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="meetings_report.pdf"'
            response.write(pdf)
            return response
        
        except Exception as e:
            logger.error('Meeting PDF report error', exc_info=True)
            raise

    def perform_create(self, serializer):
        try:
            # Toplantı zamanı kontrolü
            start_time = serializer.validated_data.get('start_time')
            end_time = serializer.validated_data.get('end_time')
            room = serializer.validated_data.get('location')

            if start_time >= end_time:
                raise InvalidMeetingTimeError('Başlangıç zamanı bitiş zamanından önce olmalıdır.')

            # Oda müsaitlik kontrolü
            conflicting_meetings = Meeting.objects.filter(
                location=room,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exists()

            if conflicting_meetings:
                raise MeetingConflictError()

            logger.info(
                'Yeni toplantı oluşturuluyor',
                extra={
                    'user': str(self.request.user),
                    'room': room.name,
                    'start_time': start_time,
                    'end_time': end_time
                }
            )
            
            serializer.save()
            
        except Exception as e:
            logger.error(
                'Toplantı oluşturma hatası',
                exc_info=True,
                extra={
                    'user': str(self.request.user),
                    'data': serializer.validated_data
                }
            )
            raise

    def perform_update(self, serializer):
        try:
            instance = serializer.instance
            new_status = serializer.validated_data.get('status')
            
            # Durum değişikliği kontrolü
            if new_status and instance.status != new_status:
                valid_transitions = {
                    'PENDING': ['APPROVED', 'REJECTED', 'CANCELLED'],
                    'APPROVED': ['COMPLETED', 'CANCELLED'],
                    'REJECTED': [],
                    'CANCELLED': [],
                    'COMPLETED': []
                }
                
                if new_status not in valid_transitions.get(instance.status, []):
                    raise InvalidMeetingStatusTransition(
                        f"'{instance.status}' durumundan '{new_status}' durumuna geçiş yapılamaz."
                    )

            logger.info(
                'Toplantı güncelleniyor',
                extra={
                    'user': str(self.request.user),
                    'meeting_id': instance.id,
                    'old_status': instance.status,
                    'new_status': new_status
                }
            )
            
            serializer.save()
            
        except Exception as e:
            logger.error(
                'Toplantı güncelleme hatası',
                exc_info=True,
                extra={
                    'user': str(self.request.user),
                    'meeting_id': instance.id,
                    'data': serializer.validated_data
                }
            )
            raise

    def perform_destroy(self, instance):
        try:
            if instance.status not in ['PENDING', 'APPROVED']:
                raise MeetingCancellationError('Bu durumdaki toplantı silinemez.')

            logger.info(
                'Toplantı siliniyor',
                extra={
                    'user': str(self.request.user),
                    'meeting_id': instance.id,
                    'status': instance.status
                }
            )
            
            instance.delete()
            
        except Exception as e:
            logger.error(
                'Toplantı silme hatası',
                exc_info=True,
                extra={
                    'user': str(self.request.user),
                    'meeting_id': instance.id
                }
            )
            raise

class MeetingRoomViewSet(viewsets.ModelViewSet):
    queryset = MeetingRoom.objects.filter(is_active=True)
    serializer_class = MeetingRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'equipment']
    ordering_fields = ['name', 'capacity']

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        now = timezone.now()
        last_month = now - timezone.timedelta(days=30)

        rooms = MeetingRoom.objects.filter(is_active=True)
        room_stats = []

        for room in rooms:
            total_meetings = Meeting.objects.filter(location=room).count()
            recent_meetings = Meeting.objects.filter(
                location=room,
                start_time__gte=last_month
            ).count()
            upcoming_meetings = Meeting.objects.filter(
                location=room,
                start_time__gt=now
            ).count()

            utilization_hours = Meeting.objects.filter(
                location=room,
                start_time__gte=last_month
            ).extra(
                select={'duration': "EXTRACT(EPOCH FROM (end_time - start_time)) / 3600"}
            ).values('duration')

            total_hours = sum(item['duration'] for item in utilization_hours)

            room_stats.append({
                'room_name': room.name,
                'total_meetings': total_meetings,
                'recent_meetings': recent_meetings,
                'upcoming_meetings': upcoming_meetings,
                'utilization_hours_last_month': round(total_hours, 2)
            })

        return Response({
            'room_statistics': room_stats,
        })

class MeetingNoteViewSet(viewsets.ModelViewSet):
    queryset = MeetingNote.objects.all()
    serializer_class = MeetingNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['content']
    ordering_fields = ['created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
