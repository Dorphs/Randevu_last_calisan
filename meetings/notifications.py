from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from twilio.rest import Client
from push_notifications.models import APNSDevice, GCMDevice
import firebase_admin
from firebase_admin import messaging
import logging

logger = logging.getLogger(__name__)

def send_email_notification(subject, template_name, context, recipient_list):
    try:
        html_message = render_to_string(f'meetings/email/{template_name}.html', context)
        send_mail(
            subject=subject,
            message='',
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list
        )
        logger.info(f'Email sent to {recipient_list}')
    except Exception as e:
        logger.error('Email sending failed', exc_info=True)
        raise

def send_sms_notification(phone_number, message):
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        logger.info(f'SMS sent to {phone_number}')
        return message.sid
    except Exception as e:
        logger.error('SMS sending failed', exc_info=True)
        raise

def send_push_notification(title, message, data=None, user=None):
    try:
        # iOS devices
        if user:
            devices = APNSDevice.objects.filter(user=user)
        else:
            devices = APNSDevice.objects.all()
        
        devices.send_message(
            message={"title": title, "body": message, "data": data or {}}
        )

        # Android devices
        if user:
            devices = GCMDevice.objects.filter(user=user)
        else:
            devices = GCMDevice.objects.all()
        
        devices.send_message(
            message={"title": title, "body": message, "data": data or {}}
        )
        
        logger.info('Push notification sent')
    except Exception as e:
        logger.error('Push notification failed', exc_info=True)
        raise

def send_meeting_notification(meeting, notification_type):
    context = {
        'meeting': meeting,
        'visitor': meeting.visitor,
        'location': meeting.location
    }
    
    if notification_type == 'created':
        # Email to visitor
        send_email_notification(
            'Toplantı Oluşturuldu',
            'meeting_created',
            context,
            [meeting.visitor.email]
        )
        
        # SMS to visitor
        if meeting.visitor.phone:
            message = f'Toplantınız oluşturuldu: {meeting.title} - {meeting.start_time}'
            send_sms_notification(meeting.visitor.phone, message)
        
        # Push notification
        send_push_notification(
            'Yeni Toplantı',
            f'Yeni toplantı oluşturuldu: {meeting.title}',
            data={'meeting_id': meeting.id}
        )
    
    elif notification_type == 'reminder':
        # Email reminder
        send_email_notification(
            'Toplantı Hatırlatması',
            'meeting_reminder',
            context,
            [meeting.visitor.email]
        )
        
        # SMS reminder
        if meeting.visitor.phone:
            message = f'Toplantı hatırlatması: {meeting.title} - {meeting.start_time}'
            send_sms_notification(meeting.visitor.phone, message)
        
        # Push notification
        send_push_notification(
            'Toplantı Hatırlatması',
            f'Yaklaşan toplantı: {meeting.title}',
            data={'meeting_id': meeting.id}
        )
    
    elif notification_type == 'cancelled':
        # Email notification
        send_email_notification(
            'Toplantı İptali',
            'meeting_cancelled',
            context,
            [meeting.visitor.email]
        )
        
        # SMS notification
        if meeting.visitor.phone:
            message = f'Toplantı iptal edildi: {meeting.title}'
            send_sms_notification(meeting.visitor.phone, message)
        
        # Push notification
        send_push_notification(
            'Toplantı İptali',
            f'Toplantı iptal edildi: {meeting.title}',
            data={'meeting_id': meeting.id}
        )
