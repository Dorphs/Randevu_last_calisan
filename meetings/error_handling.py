from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class DetailedValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Geçersiz veri.')
    default_code = 'invalid'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        
        # Hata detaylarını zenginleştir
        if isinstance(detail, dict):
            self.detail = {
                'code': code,
                'message': self.default_detail,
                'fields': detail,
                'suggestions': self._get_suggestions(detail)
            }
        else:
            self.detail = {
                'code': code,
                'message': str(detail),
                'suggestions': []
            }

    def _get_suggestions(self, errors):
        suggestions = []
        for field, error in errors.items():
            if field == 'start_time':
                suggestions.append(_('Başlangıç zamanı gelecekte olmalıdır'))
            elif field == 'end_time':
                suggestions.append(_('Bitiş zamanı başlangıç zamanından sonra olmalıdır'))
            elif field == 'location':
                suggestions.append(_('Seçilen toplantı odası bu saatlerde müsait değil'))
        return suggestions

class MeetingConflictError(DetailedValidationError):
    def __init__(self, meeting=None):
        detail = {
            'code': 'meeting_conflict',
            'message': _('Toplantı çakışması tespit edildi.'),
            'conflict_details': {
                'existing_meeting': {
                    'id': meeting.id,
                    'title': meeting.title,
                    'start_time': meeting.start_time,
                    'end_time': meeting.end_time
                } if meeting else None
            },
            'suggestions': [
                _('Farklı bir zaman seçin'),
                _('Farklı bir toplantı odası seçin'),
                _('Mevcut toplantıyı düzenleyin')
            ]
        }
        super().__init__(detail, 'meeting_conflict')

class ParticipantUnavailableError(DetailedValidationError):
    def __init__(self, participants=None):
        detail = {
            'code': 'participant_unavailable',
            'message': _('Bazı katılımcılar bu saatlerde müsait değil.'),
            'unavailable_participants': [
                {
                    'id': p.id,
                    'name': p.name,
                    'conflict_meeting': {
                        'id': p.meetings.first().id,
                        'title': p.meetings.first().title
                    }
                } for p in participants
            ] if participants else [],
            'suggestions': [
                _('Farklı bir zaman seçin'),
                _('Katılımcı listesini güncelleyin'),
                _('Katılımcıların müsaitlik durumunu kontrol edin')
            ]
        }
        super().__init__(detail, 'participant_unavailable')

class RecurringMeetingError(DetailedValidationError):
    def __init__(self, conflicts=None):
        detail = {
            'code': 'recurring_meeting_error',
            'message': _('Tekrarlanan toplantı oluşturulurken hata.'),
            'conflicts': conflicts,
            'suggestions': [
                _('Tekrar sıklığını değiştirin'),
                _('Bitiş tarihini değiştirin'),
                _('Çakışan tarihleri atlayın')
            ]
        }
        super().__init__(detail, 'recurring_meeting_error')

def custom_exception_handler(exc, context):
    """
    Özel exception handler
    """
    response = exception_handler(exc, context)
    
    if response is None:
        if isinstance(exc, ValidationError):
            exc = DetailedValidationError(detail=exc.message_dict)
            response = exception_handler(exc, context)
    
    # Log the error
    logger.error(
        'Error occurred',
        exc_info=True,
        extra={
            'view': context['view'].__class__.__name__,
            'error': str(exc),
            'user': getattr(context['request'].user, 'email', 'anonymous')
        }
    )
    
    return response
