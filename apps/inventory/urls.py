from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InventoryItemViewSet, EquipmentViewSet, FarmInputViewSet,
    InventoryTransactionViewSet, MaintenanceRecordViewSet
)

router = DefaultRouter()
router.register(r'items', InventoryItemViewSet, basename='inventory-item')
router.register(r'equipment', EquipmentViewSet, basename='equipment')
router.register(r'inputs', FarmInputViewSet, basename='farm-input')
router.register(r'transactions', InventoryTransactionViewSet, basename='inventory-transaction')
router.register(r'maintenance', MaintenanceRecordViewSet, basename='maintenance-record')

urlpatterns = [
    path('inventory/', include(router.urls)),
]