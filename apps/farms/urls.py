from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FarmViewSet, FieldViewSet, CropViewSet, CropVarietyViewSet,
    CropCycleViewSet, SoilTestViewSet, WeatherRecordViewSet
)

router = DefaultRouter()
router.register(r'farms', FarmViewSet, basename='farm')
router.register(r'fields', FieldViewSet, basename='field')
router.register(r'crops', CropViewSet, basename='crop')
router.register(r'crop-varieties', CropVarietyViewSet, basename='cropvariety')
router.register(r'crop-cycles', CropCycleViewSet, basename='cropcycle')
router.register(r'soil-tests', SoilTestViewSet, basename='soiltest')
router.register(r'weather-records', WeatherRecordViewSet, basename='weatherrecord')

urlpatterns = [
    path('', include(router.urls)),
]