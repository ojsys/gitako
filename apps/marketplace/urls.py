from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, InputProductViewSet, ProduceProductViewSet,
    OrderViewSet, ReviewViewSet
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'inputs', InputProductViewSet, basename='input')
router.register(r'produce', ProduceProductViewSet, basename='produce')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]