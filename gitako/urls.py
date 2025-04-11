from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Gitako API",
        default_version='v1',
        description="API for Gitako Farm Management System",
        contact=openapi.Contact(email="contact@gitako.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Use the site_config URLs for the homepage
    path('', include('apps.site_config.urls')),
    # Include other app URLs as needed
    # path('accounts/', include('allauth.urls')),
    # path('api/accounts/', include('dj_rest_auth.urls')),
    # path('api/accounts/registration/', include('dj_rest_auth.registration.urls')),
]


    # path('', TemplateView.as_view(template_name='base/home.html'), name='home'),
    # path('accounts/', include('apps.accounts.urls')),
    # path('farms/', include('apps.farms.web_urls')),
    # path('activities/', include('apps.activities.web_urls')),
    # path('inventory/', include('apps.inventory.web_urls')),
    # path('financials/', include('apps.financials.web_urls')),
    # path('marketplace/', include('apps.marketplace.web_urls')),
    # path('recommendations/', include('apps.recommendations.web_urls')),


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
