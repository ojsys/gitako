import logging
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from api.exceptions import (
    ServiceUnavailableException, 
    BadRequestException,
    ResourceNotFoundException,
    ConflictException
)

logger = logging.getLogger('gitako.api')

def api_exception_handler(func):
    """
    Decorator for API view methods to standardize exception handling.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Get the view instance and request
            view = args[0]
            request = view.request
            request_id = getattr(request, 'id', 'unknown')
            
            # Log the exception
            logger.error(
                f"Exception in {func.__name__} [Request ID: {request_id}]",
                exc_info=True,
                extra={
                    'request_id': request_id,
                    'view': view.__class__.__name__,
                    'method': func.__name__,
                }
            )
            
            # Re-raise the exception to be handled by the global exception handler
            raise
    
    return wrapper

def create_error_response(message, status_code=status.HTTP_400_BAD_REQUEST, errors=None, request=None):
    """
    Create a standardized error response.
    """
    response_data = {
        'detail': message,
    }
    
    if errors:
        response_data['errors'] = errors
    
    if request and hasattr(request, 'id'):
        response_data['request_id'] = request.id
    
    return Response(response_data, status=status_code)