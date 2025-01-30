from django.db import models
from django.utils.translation import gettext_lazy as _
from .user_roles import CustomUser

class Meeting(models.Model):
    class StatusTypes(models.TextChoices):
        PLANNED = 'PLANNED', _('Planlandı')
        CONFIRMED = 'CONFIRMED', _('Onaylandı')
        IN_PROGRESS = 'IN_PROGRESS', _('Devam Ediyor')
        COMPLETED = 'COMPLETED', _('Tamamlandı')
        CANCELLED = 'CANCELLED', _('İptal Edildi')

    class MeetingTypes(models.TextChoices):
        STANDARD = 'STANDARD', _('Standart')
        RECURRING = 'RECURRING', _('Tekrarlı')
        URGENT = 'URGENT', _('Acil')

    title = models.CharField(_('Başlık'), max_length=200)
    description = models.TextField(_('Açıklama'), blank=True)
    start_time = models.DateTimeField(_('Başlangıç Zamanı'))
    end_time = models.DateTimeField(_('Bitiş Zamanı'))
    status = models.CharField(
        max_length=20,
        choices=StatusTypes.choices,
        default=StatusTypes.PLANNED
    )
    meeting_type = models.CharField(
        max_length=20,
        choices=MeetingTypes.choices,
        default=MeetingTypes.STANDARD
    )
    organizer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='organized_meetings'
    )
    participants = models.ManyToManyField(
        CustomUser,
        through='MeetingParticipant',
        related_name='meetings'
    )
    room = models.ForeignKey(
        'Room',
        on_delete=models.SET_NULL,
        null=True,
        related_name='meetings'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Toplantı')
        verbose_name_plural = _('Toplantılar')
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.title} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"

class MeetingParticipant(models.Model):
    class ParticipantStatus(models.TextChoices):
        PENDING = 'PENDING', _('Beklemede')
        ACCEPTED = 'ACCEPTED', _('Kabul Edildi')
        DECLINED = 'DECLINED', _('Reddedildi')
        TENTATIVE = 'TENTATIVE', _('Belki')

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    participant = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=ParticipantStatus.choices,
        default=ParticipantStatus.PENDING
    )
    is_required = models.BooleanField(_('Zorunlu Katılımcı'), default=True)
    response_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['meeting', 'participant']
        verbose_name = _('Toplantı Katılımcısı')
        verbose_name_plural = _('Toplantı Katılımcıları')

class RecurringMeeting(models.Model):
    class FrequencyTypes(models.TextChoices):
        DAILY = 'DAILY', _('Günlük')
        WEEKLY = 'WEEKLY', _('Haftalık')
        MONTHLY = 'MONTHLY', _('Aylık')

    meeting = models.OneToOneField(
        Meeting,
        on_delete=models.CASCADE,
        related_name='recurring_settings'
    )
    frequency = models.CharField(
        max_length=20,
        choices=FrequencyTypes.choices
    )
    repeat_until = models.DateField()
    days_of_week = models.CharField(max_length=20, blank=True)  # e.g., "1,3,5" for Mon,Wed,Fri
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Tekrarlı Toplantı')
        verbose_name_plural = _('Tekrarlı Toplantılar')
