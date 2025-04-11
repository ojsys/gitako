from django.urls import path, include
from .views import api_root

urlpatterns = [
    # API root view
    path('api1', api_root, name='api-root'),
    
    # App endpoints
    path('accounts/', include('apps.accounts.urls')),
    path('farms/', include('apps.farms.urls')),
    path('marketplace/', include('apps.marketplace.urls')),
    path('activities/', include('apps.activities.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('financials/', include('apps.financials.urls')),
    path('recommendations/', include('apps.recommendations.urls')),
    path('notifications/', include('apps.notifications.urls')),
]