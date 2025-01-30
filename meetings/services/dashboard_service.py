from django.utils import timezone
from django.db.models import Count, Avg, Q
from django.core.cache import cache
from datetime import timedelta
import pandas as pd
from ..models.reports import Dashboard, DashboardWidget
from ..models.meetings import Meeting, MeetingParticipant
from ..models.visitors import Visitor
from .export_service import ExportService

class DashboardService:
    @staticmethod
    def get_meeting_trend_data(days=30):
        """Toplantı trendi verilerini hesapla"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        meetings = Meeting.objects.filter(
            start_time__gte=start_date,
            start_time__lte=end_date
        )
        
        df = pd.DataFrame(list(meetings.values('start_time')))
        df['date'] = pd.to_datetime(df['start_time']).dt.date
        daily_counts = df.groupby('date').size().reset_index()
        
        return {
            'labels': daily_counts['date'].dt.strftime('%d.%m').tolist(),
            'meetings': daily_counts[0].tolist()
        }
    
    @staticmethod
    def get_meeting_status_data():
        """Toplantı durumlarının dağılımını hesapla"""
        meetings = Meeting.objects.all()
        
        return {
            'completed': meetings.filter(status=Meeting.StatusTypes.COMPLETED).count(),
            'planned': meetings.filter(status=Meeting.StatusTypes.PLANNED).count(),
            'cancelled': meetings.filter(status=Meeting.StatusTypes.CANCELLED).count()
        }
    
    @staticmethod
    def get_participant_distribution_data(days=30):
        """Katılımcı dağılımı verilerini hesapla"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        participants = MeetingParticipant.objects.filter(
            meeting__start_time__gte=start_date,
            meeting__start_time__lte=end_date
        )
        
        df = pd.DataFrame(list(participants.values(
            'meeting__start_time',
            'status'
        )))
        df['date'] = pd.to_datetime(df['meeting__start_time']).dt.date
        status_counts = df.groupby(['date', 'status']).size().unstack(fill_value=0)
        
        return {
            'labels': status_counts.index.strftime('%d.%m').tolist(),
            'participants': status_counts.values.tolist()
        }
    
    @staticmethod
    def get_meeting_duration_data():
        """Toplantı sürelerini hesapla"""
        meetings = Meeting.objects.filter(
            status=Meeting.StatusTypes.COMPLETED
        )
        
        durations = []
        for meeting in meetings:
            duration = (meeting.end_time - meeting.start_time).total_seconds() / 60
            durations.append(duration)
        
        df = pd.DataFrame({'duration': durations})
        duration_bins = pd.cut(df['duration'], bins=5)
        duration_counts = duration_bins.value_counts().sort_index()
        
        return {
            'labels': [f'{int(b.left)}-{int(b.right)}dk' for b in duration_counts.index],
            'durations': duration_counts.values.tolist()
        }
    
    @staticmethod
    def get_visitor_trend_data(days=30):
        """Ziyaretçi trendi verilerini hesapla"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        visitors = Visitor.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        df = pd.DataFrame(list(visitors.values('created_at')))
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        daily_counts = df.groupby('date').size().reset_index()
        
        return {
            'labels': daily_counts['date'].dt.strftime('%d.%m').tolist(),
            'visitors': daily_counts[0].tolist()
        }
    
    @staticmethod
    def refresh_widget(widget):
        """Widget verilerini yenile"""
        cache_key = f'widget_data_{widget.id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
            
        data = {}
        if widget.widget_type == 'MEETING_TREND':
            data = DashboardService.get_meeting_trend_data()
        elif widget.widget_type == 'MEETING_STATUS':
            data = DashboardService.get_meeting_status_data()
        elif widget.widget_type == 'PARTICIPANT_DISTRIBUTION':
            data = DashboardService.get_participant_distribution_data()
        elif widget.widget_type == 'MEETING_DURATION':
            data = DashboardService.get_meeting_duration_data()
        elif widget.widget_type == 'VISITOR_TREND':
            data = DashboardService.get_visitor_trend_data()
            
        cache.set(cache_key, data, timeout=300)  # 5 dakika cache
        return data
    
    @staticmethod
    def update_widget_position(widget, position):
        """Widget pozisyonunu güncelle"""
        widget.position = position
        widget.save()
    
    @staticmethod
    def share_dashboard(dashboard, user_ids):
        """Dashboard'u kullanıcılarla paylaş"""
        dashboard.shared_with.add(*user_ids)
        dashboard.save()
    
    @staticmethod
    def export_dashboard(dashboard, format='excel'):
        """Dashboard verilerini dışa aktar"""
        data = {
            'dashboard_info': {
                'title': dashboard.title,
                'owner': dashboard.owner.get_full_name(),
                'created_at': dashboard.created_at,
                'updated_at': dashboard.updated_at
            },
            'widgets': []
        }
        
        for widget in dashboard.widgets.all():
            widget_data = DashboardService.refresh_widget(widget)
            data['widgets'].append({
                'title': widget.title,
                'type': widget.widget_type,
                'data': widget_data
            })
            
        return ExportService.export_data(data, format)
    
    @staticmethod
    def export_widget(widget, format='excel'):
        """Widget verilerini dışa aktar"""
        data = {
            'widget_info': {
                'title': widget.title,
                'type': widget.widget_type,
                'dashboard': widget.dashboard.title,
                'last_refresh': timezone.now()
            },
            'data': DashboardService.refresh_widget(widget)
        }
        
        return ExportService.export_data(data, format)
