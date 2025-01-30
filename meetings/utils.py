import logging
import traceback
from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.http import Http404
from rest_framework import status

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Global exception handler for API views.
    Logs errors and returns appropriate response.
    """
    # İlk olarak DRF'nin kendi exception handler'ını çağır
    response = exception_handler(exc, context)

    # Eğer response None ise, beklenmeyen bir hata var demektir
    if response is None:
        if isinstance(exc, ValidationError):
            data = {
                'error': 'Validation Error',
                'detail': exc.message_dict if hasattr(exc, 'message_dict') else str(exc),
                'code': 'validation_error'
            }
            response = Response(data, status=status.HTTP_400_BAD_REQUEST)
        
        elif isinstance(exc, Http404):
            data = {
                'error': 'Not Found',
                'detail': str(exc),
                'code': 'not_found'
            }
            response = Response(data, status=status.HTTP_404_NOT_FOUND)
        
        else:
            # Beklenmeyen hatalar için
            error_id = logger.error(
                f'Unexpected error in {context["view"].__class__.__name__}',
                exc_info=True,
                extra={
                    'view': context['view'].__class__.__name__,
                    'traceback': traceback.format_exc()
                }
            )
            
            data = {
                'error': 'Internal Server Error',
                'detail': 'Beklenmeyen bir hata oluştu.',
                'error_id': str(error_id),
                'code': 'internal_error'
            }
            response = Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Hata detaylarını logla
    logger.error(
        f'API Error: {exc.__class__.__name__}',
        extra={
            'status_code': response.status_code,
            'view': context['view'].__class__.__name__,
            'error_detail': response.data,
            'request_path': context['request'].path,
            'request_method': context['request'].method,
            'request_user': str(context['request'].user),
        }
    )

    return response
