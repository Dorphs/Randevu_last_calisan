from rest_framework.exceptions import APIException
from rest_framework import status

class MeetingConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Bu zaman diliminde toplantı odası dolu.'
    default_code = 'meeting_conflict'

class RoomNotAvailableError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Toplantı odası müsait değil.'
    default_code = 'room_not_available'

class InvalidMeetingTimeError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Geçersiz toplantı zamanı.'
    default_code = 'invalid_meeting_time'

class VisitorNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Ziyaretçi bulunamadı.'
    default_code = 'visitor_not_found'

class MeetingCancellationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Toplantı iptal edilemez.'
    default_code = 'meeting_cancellation_error'

class InvalidMeetingStatusTransition(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Geçersiz toplantı durum değişikliği.'
    default_code = 'invalid_status_transition'
