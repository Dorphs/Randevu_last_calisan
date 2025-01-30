from datetime import datetime, timedelta
import pandas as pd
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from ..models.reports import Report, ReportExecution, Dashboard
from ..models.meetings import Meeting, MeetingParticipant
from ..models.visitors import Visitor, VisitorVisit

class ReportService:
    @staticmethod
    def generate_meeting_summary(start_date, end_date, parameters=None):
        """Toplantı özet raporu oluşturur"""
        meetings = Meeting.objects.filter(
            start_time__date__range=[start_date, end_date]
        )

        # Toplantı istatistikleri
        stats = {
            'total_meetings': meetings.count(),
            'completed_meetings': meetings.filter(status='COMPLETED').count(),
            'cancelled_meetings': meetings.filter(status='CANCELLED').count(),
            'avg_duration': meetings.aggregate(
                avg_duration=Avg('end_time' - 'start_time')
            )['avg_duration'],
        }

        # Katılımcı istatistikleri
        participant_stats = MeetingParticipant.objects.filter(
            meeting__in=meetings
        ).aggregate(
            total_participants=Count('id'),
            accepted=Count('id', filter=Q(status='ACCEPTED')),
            declined=Count('id', filter=Q(status='DECLINED')),
            pending=Count('id', filter=Q(status='PENDING'))
        )

        return {
            'stats': stats,
            'participant_stats': participant_stats,
            'meetings': meetings
        }

    @staticmethod
    def generate_visitor_analytics(start_date, end_date, parameters=None):
        """Ziyaretçi analiz raporu oluşturur"""
        visits = VisitorVisit.objects.filter(
            created_at__date__range=[start_date, end_date]
        )

        # Ziyaretçi istatistikleri
        visitor_stats = {
            'total_visits': visits.count(),
            'unique_visitors': visits.values('visitor').distinct().count(),
            'avg_visit_duration': visits.exclude(
                check_out_time__isnull=True
            ).aggregate(
                avg_duration=Avg('check_out_time' - 'check_in_time')
            )['avg_duration']
        }

        # Ziyaretçi tipleri dağılımı
        visitor_types = Visitor.objects.filter(
            visits__in=visits
        ).values('visitor_type').annotate(
            count=Count('id')
        )

        return {
            'visitor_stats': visitor_stats,
            'visitor_types': visitor_types,
            'visits': visits
        }

    @staticmethod
    def generate_room_usage(start_date, end_date, parameters=None):
        """Oda kullanım raporu oluşturur"""
        meetings = Meeting.objects.filter(
            start_time__date__range=[start_date, end_date]
        )

        # Oda kullanım istatistikleri
        room_stats = meetings.values('room').annotate(
            total_meetings=Count('id'),
            total_duration=Sum('end_time' - 'start_time'),
            avg_participants=Avg('participants__count')
        )

        # Saatlik kullanım analizi
        hourly_usage = meetings.extra(
            select={'hour': 'EXTRACT(hour FROM start_time)'}
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')

        return {
            'room_stats': room_stats,
            'hourly_usage': hourly_usage,
            'meetings': meetings
        }

    @staticmethod
    def generate_attendance_report(start_date, end_date, parameters=None):
        """Katılım raporu oluşturur"""
        participants = MeetingParticipant.objects.filter(
            meeting__start_time__date__range=[start_date, end_date]
        )

        # Katılımcı istatistikleri
        attendance_stats = participants.values('participant').annotate(
            total_meetings=Count('meeting'),
            attended=Count('id', filter=Q(status='ACCEPTED')),
            declined=Count('id', filter=Q(status='DECLINED')),
            no_response=Count('id', filter=Q(status='PENDING'))
        )

        # Departman bazlı katılım
        department_stats = participants.values(
            'participant__department'
        ).annotate(
            total_participants=Count('participant', distinct=True),
            total_meetings=Count('meeting', distinct=True),
            attendance_rate=Avg(
                Case(
                    When(status='ACCEPTED', then=1),
                    default=0,
                    output_field=FloatField(),
                )
            )
        )

        return {
            'attendance_stats': attendance_stats,
            'department_stats': department_stats,
            'participants': participants
        }

    @staticmethod
    def export_to_excel(data, report_type):
        """Rapor verilerini Excel formatına dönüştürür"""
        writer = pd.ExcelWriter(f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
        
        if report_type == Report.ReportTypes.MEETING_SUMMARY:
            # Toplantı özeti
            pd.DataFrame(data['stats']).to_excel(writer, sheet_name='Özet')
            pd.DataFrame(data['participant_stats']).to_excel(writer, sheet_name='Katılımcı İstatistikleri')
            pd.DataFrame(data['meetings'].values()).to_excel(writer, sheet_name='Toplantılar')

        elif report_type == Report.ReportTypes.VISITOR_ANALYTICS:
            # Ziyaretçi analizi
            pd.DataFrame(data['visitor_stats']).to_excel(writer, sheet_name='Özet')
            pd.DataFrame(data['visitor_types']).to_excel(writer, sheet_name='Ziyaretçi Tipleri')
            pd.DataFrame(data['visits'].values()).to_excel(writer, sheet_name='Ziyaretler')

        writer.save()
        return writer.path

    @staticmethod
    def schedule_report(report_id, frequency):
        """Rapor otomatik oluşturma zamanlaması yapar"""
        report = Report.objects.get(id=report_id)
        report.is_scheduled = True
        report.schedule_frequency = frequency
        report.save()

        # Celery task'i oluştur
        if frequency == 'daily':
            schedule_time = timezone.now() + timedelta(days=1)
        elif frequency == 'weekly':
            schedule_time = timezone.now() + timedelta(weeks=1)
        elif frequency == 'monthly':
            schedule_time = timezone.now() + timedelta(days=30)

        generate_scheduled_report.apply_async(
            args=[report_id],
            eta=schedule_time
        )

    @staticmethod
    def create_dashboard_widget(dashboard_id, widget_data):
        """Dashboard widget'ı oluşturur"""
        dashboard = Dashboard.objects.get(id=dashboard_id)
        widget = DashboardWidget.objects.create(
            dashboard=dashboard,
            title=widget_data['title'],
            widget_type=widget_data['type'],
            data_source=widget_data['data_source'],
            refresh_interval=widget_data.get('refresh_interval', 0),
            position=widget_data.get('position', {})
        )
        return widget
