from django.urls import path, include

urlpatterns = [
    path('accounts/', include('apps.accounts.urls')),
    path('farms/', include('apps.farms.urls')),
    path('activities/', include('apps.activities.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('financials/', include('apps.financials.urls')),
    path('marketplace/', include('apps.marketplace.urls')),
    path('recommendations/', include('apps.recommendations.urls')),
    path('notifications/', include('apps.notifications.urls')),
]