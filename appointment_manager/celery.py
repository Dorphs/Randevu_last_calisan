import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointment_manager.settings')

app = Celery('appointment_manager')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-upcoming-meetings': {
        'task': 'meetings.tasks.check_upcoming_meetings',
        'schedule': crontab(minute='*/15'),  # Her 15 dakikada bir çalışır
    },
    'generate-daily-report': {
        'task': 'meetings.tasks.generate_daily_report',
        'schedule': crontab(hour=18, minute=0),  # Her gün saat 18:00'de çalışır
    },
}
