from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from api.views import APIDocumentationView, MetricsView, health_check

# Create schema view for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Gitako API",
        default_version='v1',
        description="API for Gitako - Smart Farm Management Platform",
        terms_of_service="https://www.gitako.com/terms/",
        contact=openapi.Contact(email="contact@gitako.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=(permissions.IsAuthenticated,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API v1 endpoints
    path('api/v1/', include('api.v1.urls')),
    
    # API documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/', APIDocumentationView.as_view(), name='api-documentation'),
    
    # Authentication URLs
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    
    # Metrics and health check endpoints
    path('metrics/', MetricsView.as_view(), name='metrics'),
    path('health/', health_check, name='health-check'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
