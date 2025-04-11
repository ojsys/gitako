import logging
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError

logger = logging.getLogger('gitako.api')

class ServiceUnavailableException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable, please try again later.'
    default_code = 'service_unavailable'

class BadRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid request.'
    default_code = 'bad_request'

class ResourceNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found.'
    default_code = 'not_found'

class ConflictException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Resource conflict.'
    default_code = 'conflict'

def custom_exception_handler(exc, context):
    """
    Custom exception handler for REST framework that improves error responses
    and logs exceptions.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If this is an unexpected exception, log it
    if response is None:
        request = context.get('request')
        request_id = getattr(request, 'id', 'unknown')
        
        # Handle Django validation errors
        if isinstance(exc, DjangoValidationError):
            data = {
                'detail': 'Validation error',
                'errors': exc.message_dict if hasattr(exc, 'message_dict') else [str(exc)],
                'request_id': request_id
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle database integrity errors
        if isinstance(exc, IntegrityError):
            data = {
                'detail': 'Database integrity error',
                'errors': [str(exc)],
                'request_id': request_id
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        
        # Log the unexpected exception
        logger.error(
            f"Unexpected exception in API view [Request ID: {request_id}]",
            exc_info=True,
            extra={
                'request_id': request_id,
                'view': context.get('view').__class__.__name__ if context.get('view') else 'unknown',
                'path': request.path if request else 'unknown',
                'method': request.method if request else 'unknown',
            }
        )
        
        # Let the middleware handle the response
        return None
    
    # Enhance the response with request ID if available
    request = context.get('request')
    if request and hasattr(request, 'id'):
        if isinstance(response.data, dict):
            response.data['request_id'] = request.id
    
    return response