from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils import timezone

class Visitor(models.Model):
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.company}"

class MeetingRoom(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    equipment = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    floor = models.CharField(max_length=50, blank=True)
    room_number = models.CharField(max_length=20, blank=True)

    def is_available(self, start_time, end_time, exclude_meeting=None):
        meetings = Meeting.objects.filter(
            location=self,
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        if exclude_meeting:
            meetings = meetings.exclude(pk=exclude_meeting.pk)
        return not meetings.exists()

    def __str__(self):
        return self.name

class Meeting(models.Model):
    MEETING_TYPES = [
        ('SCHEDULED', 'Planlı Görüşme'),
        ('UNSCHEDULED', 'Plansız Görüşme'),
        ('EXTERNAL', 'Dış Ziyaret'),
        ('INTERNAL', 'İç Toplantı'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Beklemede'),
        ('APPROVED', 'Onaylandı'),
        ('COMPLETED', 'Tamamlandı'),
        ('CANCELLED', 'İptal Edildi'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Düşük'),
        ('MEDIUM', 'Orta'),
        ('HIGH', 'Yüksek'),
    ]

    RECURRENCE_CHOICES = [
        ('NONE', 'Tekrar Yok'),
        ('DAILY', 'Günlük'),
        ('WEEKLY', 'Haftalık'),
        ('MONTHLY', 'Aylık'),
    ]

    title = models.CharField(max_length=200)
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='meetings')
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.ForeignKey(MeetingRoom, on_delete=models.SET_NULL, null=True, blank=True)
    external_location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    agenda = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_meetings')
    participants = models.ManyToManyField(User, related_name='participating_meetings', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default='NONE')
    recurrence_end_date = models.DateField(null=True, blank=True)
    google_calendar_event_id = models.CharField(max_length=1024, blank=True)
    reminder_sent = models.BooleanField(default=False)
    parent_meeting = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError('Başlangıç zamanı bitiş zamanından önce olmalıdır.')
        
        if self.location and not self.location.is_available(self.start_time, self.end_time, self):
            raise ValidationError('Bu toplantı odası seçilen zaman aralığında müsait değil.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.visitor.name}"

class MeetingTemplate(models.Model):
    """Toplantı şablonu"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration = models.DurationField()
    meeting_type = models.CharField(max_length=20, choices=Meeting.MEETING_TYPES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def create_meeting(self, start_time, visitor, location):
        """Şablondan toplantı oluştur"""
        return Meeting.objects.create(
            title=self.name,
            description=self.description,
            start_time=start_time,
            end_time=start_time + self.duration,
            meeting_type=self.meeting_type,
            visitor=visitor,
            location=location
        )

class RecurringMeeting(models.Model):
    """Tekrarlanan toplantı"""
    FREQUENCY_CHOICES = [
        ('DAILY', 'Günlük'),
        ('WEEKLY', 'Haftalık'),
        ('MONTHLY', 'Aylık'),
    ]
    
    meeting = models.OneToOneField(Meeting, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    repeat_until = models.DateField()
    days_of_week = models.CharField(max_length=20, blank=True)  # "1,2,3" formatında (Pazartesi=1)
    
    def create_recurring_meetings(self):
        """Tekrarlanan toplantıları oluştur"""
        current_date = self.meeting.start_time.date()
        time_of_day = self.meeting.start_time.time()
        duration = self.meeting.end_time - self.meeting.start_time
        
        while current_date <= self.repeat_until:
            if self.frequency == 'DAILY':
                current_date += timedelta(days=1)
            elif self.frequency == 'WEEKLY':
                if self.days_of_week:
                    days = [int(d) for d in self.days_of_week.split(',')]
                    current_date += timedelta(days=1)
                    if current_date.isoweekday() not in days:
                        continue
                else:
                    current_date += timedelta(days=7)
            elif self.frequency == 'MONTHLY':
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            
            start_time = datetime.combine(current_date, time_of_day)
            Meeting.objects.create(
                title=self.meeting.title,
                description=self.meeting.description,
                start_time=start_time,
                end_time=start_time + duration,
                meeting_type=self.meeting.meeting_type,
                visitor=self.meeting.visitor,
                location=self.meeting.location,
                parent_meeting=self.meeting
            )

class MeetingAttachment(models.Model):
    """Toplantı ekleri"""
    meeting = models.ForeignKey(Meeting, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='meeting_attachments/%Y/%m/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    file_size = models.IntegerField()  # bytes
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.file_name:
            self.file_name = self.file.name
        if not self.file_size:
            self.file_size = self.file.size
        if not self.file_type:
            self.file_type = self.file.content_type
        super().save(*args, **kwargs)

class MeetingNote(models.Model):
    """Toplantı notları"""
    meeting = models.ForeignKey(Meeting, related_name='notes', on_delete=models.CASCADE)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_private = models.BooleanField(default=False)

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Oluşturma'),
        ('UPDATE', 'Güncelleme'),
        ('DELETE', 'Silme'),
        ('STATUS_CHANGE', 'Durum Değişikliği'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.meeting.title}"
