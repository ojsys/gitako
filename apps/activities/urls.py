from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ActivityViewSet, PlantingActivityViewSet, FertilizerActivityViewSet,
    PestControlActivityViewSet, IrrigationActivityViewSet, HarvestActivityViewSet,
    ActivityReminderViewSet
)

router = DefaultRouter()
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'planting', PlantingActivityViewSet, basename='planting')
router.register(r'fertilizer', FertilizerActivityViewSet, basename='fertilizer')
router.register(r'pest-control', PestControlActivityViewSet, basename='pestcontrol')
router.register(r'irrigation', IrrigationActivityViewSet, basename='irrigation')
router.register(r'harvest', HarvestActivityViewSet, basename='harvest')
router.register(r'reminders', ActivityReminderViewSet, basename='reminder')

urlpatterns = [
    path('', include(router.urls)),
]