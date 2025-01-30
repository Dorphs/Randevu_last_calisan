from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from ...models import Meeting, Visitor, MeetingRoom
from ...serializers import MeetingSerializer, VisitorSerializer
from ...notifications import send_meeting_notification
import logging
from datetime import datetime, timedelta
from django.db.models import Q

logger = logging.getLogger(__name__)

class MobileVisitorViewSet(viewsets.ModelViewSet):
    serializer_class = VisitorSerializer
    
    def get_queryset(self):
        return Visitor.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        visitor = self.get_queryset().first()
        if visitor:
            serializer = self.get_serializer(visitor)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

class MobileMeetingViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingSerializer
    
    def get_queryset(self):
        queryset = Meeting.objects.filter(visitor__user=self.request.user)
        
        # Filtreleme seçenekleri
        status = self.request.query_params.get('status', None)
        date = self.request.query_params.get('date', None)
        
        if status:
            queryset = queryset.filter(status=status)
        if date:
            queryset = queryset.filter(start_time__date=date)
            
        return queryset.order_by('start_time')
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        now = timezone.now()
        meetings = self.get_queryset().filter(
            start_time__gt=now,
            status='APPROVED'
        ).order_by('start_time')[:5]
        
        serializer = self.get_serializer(meetings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        today = timezone.now().date()
        meetings = self.get_queryset().filter(
            start_time__date=today
        ).order_by('start_time')
        
        serializer = self.get_serializer(meetings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        meeting = self.get_object()
        
        if meeting.status not in ['PENDING', 'APPROVED']:
            return Response(
                {'detail': 'Bu toplantı iptal edilemez.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        meeting.status = 'CANCELLED'
        meeting.save()
        
        # Bildirim gönder
        send_meeting_notification(meeting, 'cancelled')
        
        return Response({'status': 'cancelled'})
    
    @action(detail=True, methods=['post'])
    def register_device(self, request, pk=None):
        device_token = request.data.get('device_token')
        device_type = request.data.get('device_type')  # 'ios' or 'android'
        
        if not device_token or not device_type:
            return Response(
                {'detail': 'device_token ve device_type gerekli.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if device_type == 'ios':
                APNSDevice.objects.get_or_create(
                    registration_id=device_token,
                    user=request.user
                )
            else:
                GCMDevice.objects.get_or_create(
                    registration_id=device_token,
                    user=request.user
                )
            
            return Response({'status': 'registered'})
            
        except Exception as e:
            logger.error('Device registration failed', exc_info=True)
            return Response(
                {'detail': 'Cihaz kaydı başarısız.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def calendar_view(self, request):
        """Takvim görünümü için toplantıları döndür"""
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        meetings = self.get_queryset().filter(
            start_time__year=year,
            start_time__month=month
        ).order_by('start_time')
        
        serializer = self.get_serializer(meetings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def week_view(self, request):
        """Haftalık görünüm için toplantıları döndür"""
        date = request.query_params.get('date')
        if date:
            start_date = datetime.strptime(date, '%Y-%m-%d').date()
            end_date = start_date + timedelta(days=7)
            
            meetings = self.get_queryset().filter(
                start_time__date__range=[start_date, end_date]
            ).order_by('start_time')
            
            serializer = self.get_serializer(meetings, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """Toplantıyı yeniden planla"""
        meeting = self.get_object()
        new_start_time = request.data.get('new_start_time')
        new_end_time = request.data.get('new_end_time')
        
        if not new_start_time or not new_end_time:
            return Response(
                {'detail': 'Yeni başlangıç ve bitiş zamanı gerekli.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Çakışma kontrolü
        if Meeting.objects.filter(
            location=meeting.location,
            start_time__lt=new_end_time,
            end_time__gt=new_start_time
        ).exclude(id=meeting.id).exists():
            return Response(
                {'detail': 'Bu zaman diliminde toplantı odası dolu.'},
                status=status.HTTP_409_CONFLICT
            )
        
        meeting.start_time = new_start_time
        meeting.end_time = new_end_time
        meeting.save()
        
        # Bildirim gönder
        send_meeting_notification(meeting, 'rescheduled')
        
        serializer = self.get_serializer(meeting)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Toplantılarda arama yap"""
        query = request.query_params.get('q', '')
        meetings = self.get_queryset().filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(visitor__name__icontains=query) |
            Q(location__name__icontains=query)
        ).order_by('-start_time')
        
        serializer = self.get_serializer(meetings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def offline_sync(self, request):
        """Offline sync için son değişiklikleri döndür"""
        last_sync = request.query_params.get('last_sync')
        if last_sync:
            meetings = self.get_queryset().filter(
                modified_at__gt=last_sync
            ).order_by('-modified_at')
            
            serializer = self.get_serializer(meetings, many=True)
            return Response({
                'meetings': serializer.data,
                'sync_time': timezone.now()
            })
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def bulk_status_update(self, request):
        """Toplu durum güncelleme"""
        updates = request.data.get('updates', [])
        results = []
        
        for update in updates:
            try:
                meeting = Meeting.objects.get(id=update['id'])
                meeting.status = update['status']
                meeting.save()
                results.append({
                    'id': meeting.id,
                    'status': 'success'
                })
            except Exception as e:
                results.append({
                    'id': update['id'],
                    'status': 'error',
                    'message': str(e)
                })
        
        return Response(results)
