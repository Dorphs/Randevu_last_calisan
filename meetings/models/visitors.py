from django.db import models
from django.utils.translation import gettext_lazy as _
from .user_roles import CustomUser

class Visitor(models.Model):
    class VisitorTypes(models.TextChoices):
        ONETIME = 'ONETIME', _('Tek Seferlik')
        REGULAR = 'REGULAR', _('Düzenli')
        VIP = 'VIP', _('VIP')

    first_name = models.CharField(_('Ad'), max_length=100)
    last_name = models.CharField(_('Soyad'), max_length=100)
    email = models.EmailField(_('E-posta'))
    phone = models.CharField(_('Telefon'), max_length=20)
    company = models.CharField(_('Şirket'), max_length=200, blank=True)
    visitor_type = models.CharField(
        max_length=20,
        choices=VisitorTypes.choices,
        default=VisitorTypes.ONETIME
    )
    identity_number = models.CharField(_('Kimlik No'), max_length=20, unique=True)
    photo = models.ImageField(upload_to='visitor_photos/', null=True, blank=True)
    is_blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Ziyaretçi')
        verbose_name_plural = _('Ziyaretçiler')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.company})"

class VisitorVisit(models.Model):
    class VisitStatus(models.TextChoices):
        SCHEDULED = 'SCHEDULED', _('Planlandı')
        CHECKED_IN = 'CHECKED_IN', _('Giriş Yapıldı')
        CHECKED_OUT = 'CHECKED_OUT', _('Çıkış Yapıldı')
        CANCELLED = 'CANCELLED', _('İptal Edildi')

    visitor = models.ForeignKey(
        Visitor,
        on_delete=models.CASCADE,
        related_name='visits'
    )
    meeting = models.ForeignKey(
        'Meeting',
        on_delete=models.CASCADE,
        related_name='visitor_visits'
    )
    host = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='hosted_visits'
    )
    status = models.CharField(
        max_length=20,
        choices=VisitStatus.choices,
        default=VisitStatus.SCHEDULED
    )
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    badge_number = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Ziyaretçi Ziyareti')
        verbose_name_plural = _('Ziyaretçi Ziyaretleri')
        ordering = ['-created_at']

class VisitorDocument(models.Model):
    visitor = models.ForeignKey(
        Visitor,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(max_length=50)
    file = models.FileField(upload_to='visitor_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='verified_documents'
    )

    class Meta:
        verbose_name = _('Ziyaretçi Dokümanı')
        verbose_name_plural = _('Ziyaretçi Dokümanları')
