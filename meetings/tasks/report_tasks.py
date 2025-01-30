from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from ..models.reports import Report, ReportExecution
from ..services.report_service import ReportService

@shared_task
def generate_scheduled_report(report_id):
    """Zamanlanmış rapor oluşturma"""
    try:
        report = Report.objects.get(id=report_id)
        
        # Rapor parametrelerini hazırla
        start_date = report.parameters.get('start_date')
        end_date = report.parameters.get('end_date')
        
        # Rapor tipine göre veri üret
        if report.report_type == Report.ReportTypes.MEETING_SUMMARY:
            data = ReportService.generate_meeting_summary(start_date, end_date)
        elif report.report_type == Report.ReportTypes.VISITOR_ANALYTICS:
            data = ReportService.generate_visitor_analytics(start_date, end_date)
        elif report.report_type == Report.ReportTypes.ROOM_USAGE:
            data = ReportService.generate_room_usage(start_date, end_date)
        elif report.report_type == Report.ReportTypes.ATTENDANCE:
            data = ReportService.generate_attendance_report(start_date, end_date)
        
        # Excel dosyası oluştur
        file_path = ReportService.export_to_excel(data, report.report_type)
        
        # Rapor çalıştırma kaydı oluştur
        execution = ReportExecution.objects.create(
            report=report,
            status=ReportExecution.StatusTypes.COMPLETED,
            result_file=file_path
        )
        
        # Raporu mail ile gönder
        for recipient in report.recipients.all():
            send_report_email.delay(
                recipient.email,
                report.title,
                file_path
            )
        
        # Bir sonraki çalıştırma için zamanla
        if report.is_scheduled:
            schedule_next_report.delay(report_id)
            
    except Exception as e:
        # Hata durumunda log oluştur
        ReportExecution.objects.create(
            report_id=report_id,
            status=ReportExecution.StatusTypes.FAILED,
            error_message=str(e)
        )

@shared_task
def send_report_email(recipient_email, report_title, file_path):
    """Raporu email ile gönderir"""
    try:
        subject = f'Rapor: {report_title}'
        message = f'Ekteki raporu inceleyebilirsiniz: {report_title}'
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
            attachments=[(file_path.split('/')[-1], open(file_path, 'rb').read())]
        )
    except Exception as e:
        print(f"Email gönderme hatası: {str(e)}")

@shared_task
def schedule_next_report(report_id):
    """Bir sonraki rapor çalıştırmasını zamanlar"""
    try:
        report = Report.objects.get(id=report_id)
        
        if report.schedule_frequency == 'daily':
            eta = timezone.now() + timedelta(days=1)
        elif report.schedule_frequency == 'weekly':
            eta = timezone.now() + timedelta(weeks=1)
        elif report.schedule_frequency == 'monthly':
            eta = timezone.now() + timedelta(days=30)
        
        generate_scheduled_report.apply_async(
            args=[report_id],
            eta=eta
        )
    except Report.DoesNotExist:
        print(f"Rapor bulunamadı: {report_id}")

@shared_task
def cleanup_old_reports():
    """Eski rapor dosyalarını temizler"""
    try:
        # 30 günden eski raporları temizle
        threshold_date = timezone.now() - timedelta(days=30)
        old_executions = ReportExecution.objects.filter(
            created_at__lt=threshold_date,
            result_file__isnull=False
        )
        
        for execution in old_executions:
            # Dosyayı sil
            if execution.result_file:
                execution.result_file.delete()
            
            # Kaydı güncelle
            execution.result_file = None
            execution.save()
            
    except Exception as e:
        print(f"Rapor temizleme hatası: {str(e)}")

@shared_task
def refresh_dashboard_widgets():
    """Dashboard widget'larını yeniler"""
    try:
        # Yenilenme zamanı gelmiş widget'ları bul
        widgets = DashboardWidget.objects.filter(
            refresh_interval__gt=0
        ).select_related('dashboard')
        
        for widget in widgets:
            # Widget verilerini güncelle
            if widget.widget_type == DashboardWidget.WidgetTypes.CHART:
                # Grafik verilerini güncelle
                update_chart_widget.delay(widget.id)
            elif widget.widget_type == DashboardWidget.WidgetTypes.TABLE:
                # Tablo verilerini güncelle
                update_table_widget.delay(widget.id)
            elif widget.widget_type == DashboardWidget.WidgetTypes.METRIC:
                # Metrik verilerini güncelle
                update_metric_widget.delay(widget.id)
                
    except Exception as e:
        print(f"Widget güncelleme hatası: {str(e)}")

@shared_task
def update_chart_widget(widget_id):
    """Grafik widget'ını günceller"""
    try:
        widget = DashboardWidget.objects.get(id=widget_id)
        data_source = widget.data_source
        
        # Veri kaynağına göre grafik verilerini güncelle
        if data_source.get('type') == 'meeting_summary':
            data = ReportService.generate_meeting_summary(
                data_source.get('start_date'),
                data_source.get('end_date')
            )
        elif data_source.get('type') == 'visitor_analytics':
            data = ReportService.generate_visitor_analytics(
                data_source.get('start_date'),
                data_source.get('end_date')
            )
            
        # Widget verilerini güncelle
        widget.data_source['data'] = data
        widget.save()
        
    except DashboardWidget.DoesNotExist:
        print(f"Widget bulunamadı: {widget_id}")
    except Exception as e:
        print(f"Grafik güncelleme hatası: {str(e)}")

@shared_task
def update_table_widget(widget_id):
    """Tablo widget'ını günceller"""
    try:
        widget = DashboardWidget.objects.get(id=widget_id)
        data_source = widget.data_source
        
        # Veri kaynağına göre tablo verilerini güncelle
        if data_source.get('type') == 'room_usage':
            data = ReportService.generate_room_usage(
                data_source.get('start_date'),
                data_source.get('end_date')
            )
        elif data_source.get('type') == 'attendance':
            data = ReportService.generate_attendance_report(
                data_source.get('start_date'),
                data_source.get('end_date')
            )
            
        # Widget verilerini güncelle
        widget.data_source['data'] = data
        widget.save()
        
    except DashboardWidget.DoesNotExist:
        print(f"Widget bulunamadı: {widget_id}")
    except Exception as e:
        print(f"Tablo güncelleme hatası: {str(e)}")

@shared_task
def update_metric_widget(widget_id):
    """Metrik widget'ını günceller"""
    try:
        widget = DashboardWidget.objects.get(id=widget_id)
        data_source = widget.data_source
        
        # Metrik tipine göre veri hesapla
        if data_source.get('metric_type') == 'total_meetings':
            value = Meeting.objects.filter(
                start_time__date=timezone.now().date()
            ).count()
        elif data_source.get('metric_type') == 'active_visitors':
            value = VisitorVisit.objects.filter(
                status=VisitorVisit.VisitStatus.CHECKED_IN
            ).count()
            
        # Widget verilerini güncelle
        widget.data_source['value'] = value
        widget.save()
        
    except DashboardWidget.DoesNotExist:
        print(f"Widget bulunamadı: {widget_id}")
    except Exception as e:
        print(f"Metrik güncelleme hatası: {str(e)}")
