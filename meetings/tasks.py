from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from .models import Meeting, ActivityLog
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_upcoming_meetings():
    """Yaklaşan toplantıları kontrol eder ve bildirimleri gönderir"""
    now = timezone.now()
    upcoming_meetings = Meeting.objects.filter(
        start_time__gt=now,
        start_time__lte=now + timedelta(hours=1),
        reminder_sent=False,
        status='APPROVED'
    )

    for meeting in upcoming_meetings:
        try:
            # Katılımcılara email gönder
            subject = f'Hatırlatma: {meeting.title}'
            context = {
                'meeting': meeting,
                'start_time': meeting.start_time,
                'location': meeting.location or meeting.external_location
            }
            
            html_message = render_to_string('meetings/email/reminder.html', context)
            
            recipient_list = [meeting.visitor.email] if meeting.visitor.email else []
            recipient_list.extend([p.email for p in meeting.participants.all() if p.email])
            
            if recipient_list:
                send_mail(
                    subject=subject,
                    message='',
                    html_message=html_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=recipient_list,
                    fail_silently=False,
                )
            
            meeting.reminder_sent = True
            meeting.save()
            
            logger.info(f'Reminder sent for meeting: {meeting.title}')
            
        except Exception as e:
            logger.error(f'Error sending reminder for meeting {meeting.id}: {str(e)}')

@shared_task
def generate_daily_report():
    """Günlük toplantı raporu oluşturur"""
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    
    # Bugünün toplantıları
    todays_meetings = Meeting.objects.filter(
        start_time__date=today
    ).order_by('start_time')
    
    # Yarının toplantıları
    tomorrows_meetings = Meeting.objects.filter(
        start_time__date=tomorrow
    ).order_by('start_time')
    
    context = {
        'today': today,
        'tomorrow': tomorrow,
        'todays_meetings': todays_meetings,
        'tomorrows_meetings': tomorrows_meetings
    }
    
    try:
        html_message = render_to_string('meetings/email/daily_report.html', context)
        
        send_mail(
            subject=f'Günlük Toplantı Raporu - {today}',
            message='',
            html_message=html_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        
        logger.info('Daily report generated and sent successfully')
        
    except Exception as e:
        logger.error(f'Error generating daily report: {str(e)}')

@shared_task
def create_recurring_meetings(meeting_id):
    """Tekrarlayan toplantıları oluşturur"""
    try:
        meeting = Meeting.objects.get(id=meeting_id)
        if not meeting.is_recurring or not meeting.recurrence_end_date:
            return
        
        current_date = meeting.start_time.date()
        end_date = meeting.recurrence_end_date
        
        while current_date <= end_date:
            if meeting.recurrence_pattern == 'DAILY':
                current_date += timedelta(days=1)
            elif meeting.recurrence_pattern == 'WEEKLY':
                current_date += timedelta(weeks=1)
            elif meeting.recurrence_pattern == 'MONTHLY':
                # Bir sonraki ayın aynı günü
                if current_date.month == 12:
                    next_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    next_date = current_date.replace(month=current_date.month + 1)
                current_date = next_date
            else:
                break
                
            # Yeni toplantı oluştur
            Meeting.objects.create(
                title=meeting.title,
                visitor=meeting.visitor,
                meeting_type=meeting.meeting_type,
                start_time=timezone.make_aware(datetime.combine(current_date, meeting.start_time.time())),
                end_time=timezone.make_aware(datetime.combine(current_date, meeting.end_time.time())),
                location=meeting.location,
                external_location=meeting.external_location,
                description=meeting.description,
                agenda=meeting.agenda,
                created_by=meeting.created_by,
                priority=meeting.priority
            )
            
        logger.info(f'Recurring meetings created for meeting {meeting_id}')
        
    except Meeting.DoesNotExist:
        logger.error(f'Meeting {meeting_id} not found')
    except Exception as e:
        logger.error(f'Error creating recurring meetings for {meeting_id}: {str(e)}')
