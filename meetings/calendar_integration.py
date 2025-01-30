from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from O365 import Account
from datetime import datetime, timedelta
import json
import os

class CalendarIntegration:
    """Base class for calendar integrations"""
    def create_event(self, meeting):
        raise NotImplementedError
    
    def update_event(self, meeting):
        raise NotImplementedError
    
    def delete_event(self, meeting):
        raise NotImplementedError
    
    def get_free_busy(self, start_time, end_time):
        raise NotImplementedError

class GoogleCalendarIntegration(CalendarIntegration):
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, credentials_path='credentials.json', token_path='token.json'):
        self.credentials = None
        self.credentials_path = credentials_path
        self.token_path = token_path
        self._authenticate()
    
    def _authenticate(self):
        if os.path.exists(self.token_path):
            self.credentials = Credentials.from_authorized_user_file(
                self.token_path, self.SCOPES)
        
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                self.credentials = flow.run_local_server(port=0)
            
            with open(self.token_path, 'w') as token:
                token.write(self.credentials.to_json())
    
    def create_event(self, meeting):
        service = build('calendar', 'v3', credentials=self.credentials)
        
        event = {
            'summary': meeting.title,
            'location': meeting.location.name,
            'description': meeting.description,
            'start': {
                'dateTime': meeting.start_time.isoformat(),
                'timeZone': 'Europe/Istanbul',
            },
            'end': {
                'dateTime': meeting.end_time.isoformat(),
                'timeZone': 'Europe/Istanbul',
            },
            'attendees': [
                {'email': meeting.visitor.email}
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }
        
        if meeting.is_recurring:
            recurrence = meeting.recurring_meeting
            event['recurrence'] = [
                f'RRULE:FREQ={recurrence.frequency};'
                f'UNTIL={recurrence.repeat_until.strftime("%Y%m%dT235959Z")}'
            ]
            if recurrence.days_of_week:
                event['recurrence'][0] += f';BYDAY={recurrence.days_of_week}'
        
        event = service.events().insert(calendarId='primary', body=event).execute()
        return event['id']
    
    def update_event(self, meeting):
        service = build('calendar', 'v3', credentials=self.credentials)
        
        event = service.events().get(
            calendarId='primary',
            eventId=meeting.google_calendar_event_id
        ).execute()
        
        event['summary'] = meeting.title
        event['location'] = meeting.location.name
        event['description'] = meeting.description
        event['start']['dateTime'] = meeting.start_time.isoformat()
        event['end']['dateTime'] = meeting.end_time.isoformat()
        
        updated_event = service.events().update(
            calendarId='primary',
            eventId=meeting.google_calendar_event_id,
            body=event
        ).execute()
        
        return updated_event['id']
    
    def delete_event(self, meeting):
        service = build('calendar', 'v3', credentials=self.credentials)
        service.events().delete(
            calendarId='primary',
            eventId=meeting.google_calendar_event_id
        ).execute()
    
    def get_free_busy(self, start_time, end_time):
        service = build('calendar', 'v3', credentials=self.credentials)
        
        body = {
            "timeMin": start_time.isoformat(),
            "timeMax": end_time.isoformat(),
            "items": [{"id": "primary"}]
        }
        
        events_result = service.freebusy().query(body=body).execute()
        return events_result['calendars']['primary']['busy']

class OutlookCalendarIntegration(CalendarIntegration):
    def __init__(self, client_id, client_secret, tenant_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self._authenticate()
    
    def _authenticate(self):
        credentials = (self.client_id, self.client_secret)
        self.account = Account(credentials)
        self.account.authenticate()
    
    def create_event(self, meeting):
        schedule = self.account.schedule()
        calendar = schedule.get_default_calendar()
        
        event = calendar.new_event()
        event.subject = meeting.title
        event.location = meeting.location.name
        event.body = meeting.description
        event.start = meeting.start_time
        event.end = meeting.end_time
        
        if meeting.is_recurring:
            recurrence = meeting.recurring_meeting
            event.recurrence.pattern = {
                'type': recurrence.frequency.lower(),
                'interval': 1,
                'daysOfWeek': recurrence.days_of_week.split(',') if recurrence.days_of_week else None,
                'firstDayOfWeek': 'monday'
            }
            event.recurrence.range = {
                'type': 'endDate',
                'startDate': meeting.start_time.date(),
                'endDate': recurrence.repeat_until
            }
        
        event.save()
        return event.object_id
    
    def update_event(self, meeting):
        schedule = self.account.schedule()
        calendar = schedule.get_default_calendar()
        event = calendar.get_event(meeting.outlook_event_id)
        
        event.subject = meeting.title
        event.location = meeting.location.name
        event.body = meeting.description
        event.start = meeting.start_time
        event.end = meeting.end_time
        
        event.save()
        return event.object_id
    
    def delete_event(self, meeting):
        schedule = self.account.schedule()
        calendar = schedule.get_default_calendar()
        event = calendar.get_event(meeting.outlook_event_id)
        event.delete()
    
    def get_free_busy(self, start_time, end_time):
        schedule = self.account.schedule()
        calendar = schedule.get_default_calendar()
        
        availability = calendar.get_availability(
            start_time,
            end_time,
            'UTC'
        )
        return availability
