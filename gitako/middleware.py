import time
import uuid
import json
import logging
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings
from prometheus_client import Counter, Histogram
import traceback


logger = logging.getLogger('gitako.api')

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    'django_http_requests_total',
    'Total count of HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'django_http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

API_ERRORS = Counter(
    'django_api_errors_total',
    'Total count of API errors',
    ['method', 'endpoint', 'status']
)

logger = logging.getLogger('gitako.analytics')

class APIAnalyticsMiddleware:
    """
    Middleware to track API usage and performance.
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip analytics for non-API requests
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.request_id = request_id
        
        # Record request start time
        start_time = time.time()
        
        # Process request
        response = self.get_response(request)
        
        # Calculate request duration
        duration = time.time() - start_time
        
        # Extract endpoint for metrics
        endpoint = self.get_endpoint_for_metrics(request.path)
        
        # Update Prometheus metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(duration)
        
        # Track API errors
        if 400 <= response.status_code < 600:
            API_ERRORS.labels(
                method=request.method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()
        
        # Log analytics data
        analytics_data = {
            'request_id': request_id,
            'timestamp': timezone.now().isoformat(),
            'method': request.method,
            'path': request.path,
            'user_id': request.user.id if request.user.is_authenticated else None,
            'status_code': response.status_code,
            'duration': duration,
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'query_params': dict(request.GET.items()),
        }
        
        # Log as JSON
        logger.info(json.dumps(analytics_data))
        
        # Add request ID to response headers
        response['X-Request-ID'] = request_id
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_endpoint_for_metrics(self, path):
        """
        Extract a generic endpoint name from the path for metrics.
        This prevents high cardinality in metrics.
        """
        parts = path.strip('/').split('/')
        
        # Handle API versioning
        if len(parts) >= 2 and parts[0] == 'api' and parts[1].startswith('v'):
            # Remove API version
            parts = ['api'] + parts[2:]
        
        # Handle detail views (with IDs)
        for i, part in enumerate(parts):
            if part.isdigit() or (part and part[0].isdigit()):
                parts[i] = ':id'
        
        # Limit depth to prevent high cardinality
        if len(parts) > 4:
            parts = parts[:4] + ['...']
        
        return '/' + '/'.join(parts)



class RequestIDMiddleware:
    """
    Middleware that adds a unique request ID to each request.
    This helps with tracing requests through logs.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = str(uuid.uuid4())
        request.id = request_id
        
        # Add the request ID to the response headers
        response = self.get_response(request)
        response['X-Request-ID'] = request_id
        
        return response

class ExceptionMiddleware:
    """
    Middleware that handles exceptions and returns appropriate responses.
    Also logs exceptions for monitoring and debugging.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        # Generate a unique error ID
        error_id = str(uuid.uuid4())
        
        # Get the request ID if available
        request_id = getattr(request, 'id', 'unknown')
        
        # Log the exception with details
        logger.error(
            f"Exception occurred [Error ID: {error_id}] [Request ID: {request_id}]",
            exc_info=True,
            extra={
                'error_id': error_id,
                'request_id': request_id,
                'user_id': request.user.id if request.user.is_authenticated else None,
                'path': request.path,
                'method': request.method,
                'query_params': dict(request.GET.items()),
            }
        )
        
        # Prepare the response based on the environment
        if settings.DEBUG:
            # In development, include more details
            response_data = {
                'error': str(exception),
                'error_id': error_id,
                'request_id': request_id,
                'traceback': traceback.format_exc(),
            }
        else:
            # In production, keep it simple
            response_data = {
                'error': 'An unexpected error occurred',
                'error_id': error_id,
                'request_id': request_id,
            }
        
        # Return a JSON response
        return JsonResponse(response_data, status=500)

class APILoggingMiddleware:
    """
    Middleware that logs API requests and responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip logging for non-API requests
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        # Get request details
        request_id = getattr(request, 'id', str(uuid.uuid4()))
        method = request.method
        path = request.path
        query_params = dict(request.GET.items())
        
        # Log the request
        logger.info(
            f"API Request: {method} {path}",
            extra={
                'request_id': request_id,
                'method': method,
                'path': path,
                'query_params': query_params,
                'user_id': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
            }
        )
        
        # Process the request
        response = self.get_response(request)
        
        # Log the response
        logger.info(
            f"API Response: {method} {path} {response.status_code}",
            extra={
                'request_id': request_id,
                'method': method,
                'path': path,
                'status_code': response.status_code,
                'response_time': getattr(request, '_start_time', 0),
            }
        )
        
        return response