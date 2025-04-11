from django.urls import path
from . import web_views

app_name = 'farms'

urlpatterns = [
    path('farms/', web_views.farm_list, name='list'),
    path('create/', web_views.farm_create, name='create'),
    path('<int:pk>/', web_views.farm_detail, name='detail'),
    path('<int:pk>/edit/', web_views.farm_edit, name='edit'),
    path('<int:pk>/delete/', web_views.farm_delete, name='delete'),
    path('<int:farm_id>/fields/', web_views.field_list, name='field_list'),
    path('<int:farm_id>/fields/create/', web_views.field_create, name='field_create'),
    path('fields/<int:pk>/', web_views.field_detail, name='field_detail'),
    path('fields/<int:pk>/edit/', web_views.field_edit, name='field_edit'),
    path('fields/<int:pk>/delete/', web_views.field_delete, name='field_delete'),
]