from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import JSONField
from .user_roles import CustomUser

class Report(models.Model):
    class ReportTypes(models.TextChoices):
        MEETING_SUMMARY = 'MEETING_SUMMARY', _('Toplantı Özeti')
        VISITOR_ANALYTICS = 'VISITOR_ANALYTICS', _('Ziyaretçi Analizi')
        ROOM_USAGE = 'ROOM_USAGE', _('Oda Kullanımı')
        ATTENDANCE = 'ATTENDANCE', _('Katılım Raporu')
        CUSTOM = 'CUSTOM', _('Özel Rapor')

    title = models.CharField(_('Başlık'), max_length=200)
    report_type = models.CharField(
        max_length=20,
        choices=ReportTypes.choices
    )
    parameters = JSONField(default=dict)  # Rapor parametreleri
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='created_reports'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_scheduled = models.BooleanField(default=False)  # Otomatik oluşturma
    schedule_frequency = models.CharField(max_length=20, blank=True)  # daily, weekly, monthly
    recipients = models.ManyToManyField(
        CustomUser,
        related_name='subscribed_reports'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Rapor')
        verbose_name_plural = _('Raporlar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"

class ReportExecution(models.Model):
    class StatusTypes(models.TextChoices):
        PENDING = 'PENDING', _('Bekliyor')
        IN_PROGRESS = 'IN_PROGRESS', _('İşleniyor')
        COMPLETED = 'COMPLETED', _('Tamamlandı')
        FAILED = 'FAILED', _('Başarısız')

    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    status = models.CharField(
        max_length=20,
        choices=StatusTypes.choices,
        default=StatusTypes.PENDING
    )
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    result_file = models.FileField(
        upload_to='report_results/',
        null=True,
        blank=True
    )
    error_message = models.TextField(blank=True)
    execution_parameters = JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Rapor Çalıştırma')
        verbose_name_plural = _('Rapor Çalıştırmaları')
        ordering = ['-created_at']

class ReportTemplate(models.Model):
    name = models.CharField(_('Şablon Adı'), max_length=200)
    report_type = models.CharField(
        max_length=20,
        choices=Report.ReportTypes.choices
    )
    template_file = models.FileField(upload_to='report_templates/')
    parameters_schema = JSONField(default=dict)  # Şablon parametreleri şeması
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='created_templates'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Rapor Şablonu')
        verbose_name_plural = _('Rapor Şablonları')

class Dashboard(models.Model):
    title = models.CharField(_('Başlık'), max_length=200)
    layout = JSONField(default=dict)  # Dashboard widget yerleşimi
    is_public = models.BooleanField(default=False)
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='dashboards'
    )
    shared_with = models.ManyToManyField(
        CustomUser,
        related_name='shared_dashboards'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Dashboard')
        verbose_name_plural = _('Dashboardlar')

class DashboardWidget(models.Model):
    class WidgetTypes(models.TextChoices):
        CHART = 'CHART', _('Grafik')
        TABLE = 'TABLE', _('Tablo')
        METRIC = 'METRIC', _('Metrik')
        CUSTOM = 'CUSTOM', _('Özel Widget')

    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name='widgets'
    )
    title = models.CharField(_('Başlık'), max_length=200)
    widget_type = models.CharField(
        max_length=20,
        choices=WidgetTypes.choices
    )
    data_source = JSONField(default=dict)  # Widget veri kaynağı
    refresh_interval = models.IntegerField(default=0)  # Saniye cinsinden
    position = JSONField(default=dict)  # Widget pozisyonu
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Dashboard Widget')
        verbose_name_plural = _('Dashboard Widgetları')
        ordering = ['dashboard', 'position']
