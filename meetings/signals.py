from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Meeting, ActivityLog
from .tasks import create_recurring_meetings

@receiver(post_save, sender=Meeting)
def log_meeting_activity(sender, instance, created, **kwargs):
    """Toplantı aktivitelerini loglar"""
    if created:
        action = 'CREATE'
        description = f'Toplantı oluşturuldu: {instance.title}'
    else:
        action = 'UPDATE'
        description = f'Toplantı güncellendi: {instance.title}'

    ActivityLog.objects.create(
        user=instance.created_by,
        action=action,
        meeting=instance,
        description=description
    )

    # Tekrarlayan toplantı ise
    if created and instance.is_recurring:
        create_recurring_meetings.delay(instance.id)

@receiver(pre_save, sender=Meeting)
def log_status_change(sender, instance, **kwargs):
    """Toplantı durumu değişikliklerini loglar"""
    try:
        old_instance = Meeting.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            ActivityLog.objects.create(
                user=instance.created_by,
                action='STATUS_CHANGE',
                meeting=instance,
                description=f'Durum değiştirildi: {old_instance.get_status_display()} -> {instance.get_status_display()}'
            )
    except Meeting.DoesNotExist:
        pass

@receiver(post_delete, sender=Meeting)
def log_meeting_deletion(sender, instance, **kwargs):
    """Toplantı silme işlemlerini loglar"""
    ActivityLog.objects.create(
        user=instance.created_by,
        action='DELETE',
        meeting=instance,
        description=f'Toplantı silindi: {instance.title}'
    )
