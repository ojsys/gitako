import time
import uuid
import json
import logging
from django.utils import timezone
from django.conf import settings
from prometheus_client import Counter, Histogram

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