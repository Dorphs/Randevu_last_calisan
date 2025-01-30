from django.contrib import admin
from .models import Visitor, Meeting, MeetingRoom, MeetingNote

# Register your models here.

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'phone', 'email', 'created_at')
    search_fields = ('name', 'company', 'phone', 'email')
    list_filter = ('created_at',)

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'visitor', 'meeting_type', 'status', 'start_time', 'end_time', 'location')
    list_filter = ('meeting_type', 'status', 'start_time')
    search_fields = ('title', 'visitor__name', 'location')
    date_hierarchy = 'start_time'

@admin.register(MeetingRoom)
class MeetingRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(MeetingNote)
class MeetingNoteAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'created_by', 'created_at')
    list_filter = ('created_at', 'created_by')
    search_fields = ('meeting__title', 'content')
