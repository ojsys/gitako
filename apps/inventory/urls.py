from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InputInventoryViewSet, ProduceInventoryViewSet, InventoryTransactionViewSet
)

router = DefaultRouter()
router.register(r'inputs', InputInventoryViewSet, basename='input-inventory')
router.register(r'produce', ProduceInventoryViewSet, basename='produce-inventory')
router.register(r'transactions', InventoryTransactionViewSet, basename='inventory-transaction')

urlpatterns = [
    path('', include(router.urls)),
]