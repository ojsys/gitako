from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RecommendationViewSet, RecommendationCategoryViewSet,
    RecommendationFeedbackViewSet
)

router = DefaultRouter()
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')
router.register(r'categories', RecommendationCategoryViewSet, basename='recommendation-category')
router.register(r'feedback', RecommendationFeedbackViewSet, basename='recommendation-feedback')

urlpatterns = [
    path('', include(router.urls)),
]