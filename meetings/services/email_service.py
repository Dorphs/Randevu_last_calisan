from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from ..models.reports import Report, Dashboard

class EmailService:
    @staticmethod
    def send_report_ready_email(user, report, stats=None):
        """Rapor hazır olduğunda bildirim gönderir"""
        context = {
            'user': user,
            'report': report,
            'stats': stats,
            'report_url': f"{settings.BASE_URL}{reverse('report-detail', args=[report.id])}"
        }
        
        html_content = render_to_string('emails/report_ready.html', context)
        text_content = strip_tags(html_content)
        
        subject = f'Raporunuz Hazır: {report.title}'
        
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        
        if report.result_file:
            msg.attach_file(report.result_file.path)
            
        msg.send()

    @staticmethod
    def send_dashboard_shared_email(user, dashboard, shared_by):
        """Dashboard paylaşıldığında bildirim gönderir"""
        context = {
            'user': user,
            'dashboard': dashboard,
            'shared_by': shared_by,
            'dashboard_url': f"{settings.BASE_URL}{reverse('dashboard-detail', args=[dashboard.id])}"
        }
        
        html_content = render_to_string('emails/dashboard_shared.html', context)
        text_content = strip_tags(html_content)
        
        subject = f'Dashboard Paylaşıldı: {dashboard.title}'
        
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    @staticmethod
    def send_scheduled_report_email(user, report, stats=None, highlights=None, changes=None):
        """Zamanlanmış rapor gönderir"""
        context = {
            'user': user,
            'report': report,
            'stats': stats,
            'highlights': highlights,
            'changes': changes,
            'report_url': f"{settings.BASE_URL}{reverse('report-detail', args=[report.id])}",
            'settings_url': f"{settings.BASE_URL}{reverse('report-settings', args=[report.id])}"
        }
        
        html_content = render_to_string('emails/scheduled_report.html', context)
        text_content = strip_tags(html_content)
        
        subject = f'Zamanlanmış Rapor: {report.title}'
        
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        
        if report.result_file:
            msg.attach_file(report.result_file.path)
            
        msg.send()

    @staticmethod
    def format_changes(current_stats, previous_stats):
        """İki rapor arasındaki değişiklikleri hesaplar"""
        changes = []
        
        for key in current_stats:
            if key in previous_stats:
                current = float(current_stats[key])
                previous = float(previous_stats[key])
                
                if previous > 0:
                    percentage = ((current - previous) / previous) * 100
                    trend = 'up' if current > previous else 'down'
                    
                    changes.append({
                        'metric': key,
                        'percentage': abs(round(percentage, 1)),
                        'trend': trend
                    })
                    
        return changes

    @staticmethod
    def get_report_highlights(stats):
        """Rapordaki önemli noktaları belirler"""
        highlights = {}
        
        if 'total_meetings' in stats:
            highlights['Toplam Toplantı'] = stats['total_meetings']
            
        if 'completed_meetings' in stats and 'total_meetings' in stats:
            completion_rate = (stats['completed_meetings'] / stats['total_meetings']) * 100
            highlights['Tamamlanma Oranı'] = f'%{round(completion_rate, 1)}'
            
        if 'avg_duration' in stats:
            highlights['Ortalama Süre'] = stats['avg_duration']
            
        return highlights
