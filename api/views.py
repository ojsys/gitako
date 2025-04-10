from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from django.db import connections
from django.db.utils import OperationalError
from redis import Redis
from redis.exceptions import RedisError
import os

class APIDocumentationView(LoginRequiredMixin, TemplateView):
    """
    View for the custom API documentation page.
    """
    template_name = 'api_docs/index.html'
    login_url = '/api/auth/login/'

class MetricsView(TemplateView):
    """
    View that exposes Prometheus metrics.
    """
    def get(self, request, *args, **kwargs):
        metrics_page = generate_latest()
        return HttpResponse(
            metrics_page,
            content_type=CONTENT_TYPE_LATEST
        )

def health_check(request):
    """
    Health check endpoint for monitoring.
    Checks database and Redis connections.
    """
    # Check database connection
    db_healthy = True
    try:
        # Try to connect to the database
        connections['default'].cursor()
    except OperationalError:
        db_healthy = False
    
    # Check Redis connection if used
    redis_healthy = True
    redis_url = os.environ.get('REDIS_URL')
    if redis_url:
        try:
            redis_client = Redis.from_url(redis_url)
            redis_client.ping()
        except RedisError:
            redis_healthy = False
    
    status = 200 if (db_healthy and redis_healthy) else 503
    
    response_data = {
        'status': 'healthy' if status == 200 else 'unhealthy',
        'database': 'connected' if db_healthy else 'disconnected',
        'redis': 'connected' if redis_healthy else 'disconnected',
        'version': os.environ.get('APP_VERSION', 'unknown')
    }
    
    return JsonResponse(response_data, status=status)