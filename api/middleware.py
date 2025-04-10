import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class RequestLogMiddleware(MiddlewareMixin):
    """Middleware to log API requests and their processing time"""
    
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Only log API requests
            if request.path.startswith('/api/'):
                logger.info(
                    f"Request: {request.method} {request.path} - "
                    f"Status: {response.status_code} - "
                    f"Duration: {duration:.2f}s - "
                    f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'}"
                )
        
        return response