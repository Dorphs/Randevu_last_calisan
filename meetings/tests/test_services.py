from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from ..models.reports import Report, ReportExecution
from ..models.meetings import Meeting
from ..services.report_service import ReportService
from datetime import datetime, timedelta

User = get_user_model()

class ReportServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Test toplantıları oluştur
        self.meeting1 = Meeting.objects.create(
            title='Test Meeting 1',
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
            organizer=self.user,
            status=Meeting.StatusTypes.COMPLETED
        )
        
        self.meeting2 = Meeting.objects.create(
            title='Test Meeting 2',
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            organizer=self.user,
            status=Meeting.StatusTypes.PLANNED
        )
        
    def test_generate_meeting_summary(self):
        """Toplantı özeti oluşturma testi"""
        start_date = timezone.now().date()
        end_date = (timezone.now() + timedelta(days=7)).date()
        
        data = ReportService.generate_meeting_summary(
            start_date,
            end_date
        )
        
        self.assertIn('stats', data)
        self.assertIn('participant_stats', data)
        self.assertEqual(data['stats']['total_meetings'], 2)
        self.assertEqual(data['stats']['completed_meetings'], 1)
        
    def test_generate_visitor_analytics(self):
        """Ziyaretçi analizi oluşturma testi"""
        start_date = timezone.now().date()
        end_date = (timezone.now() + timedelta(days=7)).date()
        
        data = ReportService.generate_visitor_analytics(
            start_date,
            end_date
        )
        
        self.assertIn('visitor_stats', data)
        self.assertIn('visitor_types', data)
        
    def test_export_to_excel(self):
        """Excel export testi"""
        data = {
            'stats': {
                'total_meetings': 10,
                'completed_meetings': 8
            },
            'participant_stats': {
                'total_participants': 20,
                'accepted': 15
            }
        }
        
        file_path = ReportService.export_to_excel(
            data,
            Report.ReportTypes.MEETING_SUMMARY
        )
        
        self.assertTrue(file_path.endswith('.xlsx'))
        
    def test_schedule_report(self):
        """Rapor zamanlama testi"""
        report = Report.objects.create(
            title='Scheduled Report',
            report_type=Report.ReportTypes.MEETING_SUMMARY,
            created_by=self.user,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=7)).date()
        )
        
        ReportService.schedule_report(report.id, 'daily')
        
        report.refresh_from_db()
        self.assertTrue(report.is_scheduled)
        self.assertEqual(report.schedule_frequency, 'daily')

class DashboardServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.dashboard = Dashboard.objects.create(
            title='Test Dashboard',
            owner=self.user
        )
        
    def test_create_dashboard_widget(self):
        """Dashboard widget oluşturma testi"""
        widget_data = {
            'title': 'Test Widget',
            'type': DashboardWidget.WidgetTypes.CHART,
            'data_source': {
                'type': 'meeting_summary',
                'chart_type': 'bar'
            },
            'refresh_interval': 300
        }
        
        widget = ReportService.create_dashboard_widget(
            self.dashboard.id,
            widget_data
        )
        
        self.assertEqual(widget.title, 'Test Widget')
        self.assertEqual(widget.widget_type, DashboardWidget.WidgetTypes.CHART)
        self.assertEqual(widget.refresh_interval, 300)
        
    def test_update_chart_widget(self):
        """Chart widget güncelleme testi"""
        widget = DashboardWidget.objects.create(
            dashboard=self.dashboard,
            title='Chart Widget',
            widget_type=DashboardWidget.WidgetTypes.CHART,
            data_source={
                'type': 'meeting_summary',
                'chart_type': 'bar'
            }
        )
        
        data = ReportService.update_chart_widget(widget.id)
        
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], dict)
