from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RecommendationViewSet, CropRecommendationViewSet, RecommendedCropViewSet,
    FertilizerRecommendationViewSet, PestControlRecommendationViewSet,
    IrrigationRecommendationViewSet, MarketRecommendationViewSet
)

router = DefaultRouter()
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')
router.register(r'crop-recommendations', CropRecommendationViewSet, basename='crop-recommendation')
router.register(r'recommended-crops', RecommendedCropViewSet, basename='recommended-crop')
router.register(r'fertilizer-recommendations', FertilizerRecommendationViewSet, basename='fertilizer-recommendation')
router.register(r'pest-control-recommendations', PestControlRecommendationViewSet, basename='pest-control-recommendation')
router.register(r'irrigation-recommendations', IrrigationRecommendationViewSet, basename='irrigation-recommendation')
router.register(r'market-recommendations', MarketRecommendationViewSet, basename='market-recommendation')

urlpatterns = [
    path('', include(router.urls)),
]