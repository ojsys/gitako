from django.urls import path
from .views import HomeView

app_name = 'site_config'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
]