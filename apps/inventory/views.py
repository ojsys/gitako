from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import InventoryItem, Equipment, FarmInput, InventoryTransaction, MaintenanceRecord
from .serializers import (
    InventoryItemSerializer, EquipmentSerializer, FarmInputSerializer,
    InventoryTransactionSerializer, MaintenanceRecordSerializer
)
from api.permissions import IsResourceOwner


class InventoryItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing inventory items.
    
    Inventory items represent all physical assets and inputs in the farm inventory.
    """
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsResourceOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['item_type', 'status', 'farm']
    search_fields = ['name', 'description', 'storage_location']
    ordering_fields = ['name', 'acquisition_date', 'created_at', 'quantity']
    
    def get_queryset(self):
        """Return inventory items owned by the current user"""
        return InventoryItem.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating an inventory item"""
        serializer.save(user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Get inventory items by type",
        responses={200: InventoryItemSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Filter inventory items by type"""
        item_type = request.query_params.get('type')
        if not item_type:
            return Response(
                {"error": "Type parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        items = self.get_queryset().filter(item_type=item_type)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Get inventory items by farm",
        responses={200: InventoryItemSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_farm(self, request):
        """Filter inventory items by farm"""
        farm_id = request.query_params.get('farm_id')
        if not farm_id:
            return Response(
                {"error": "farm_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        items = self.get_queryset().filter(farm_id=farm_id)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)


class EquipmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing equipment.
    
    Equipment represents machinery, tools, and other durable assets used in farming.
    """
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['inventory_item__status', 'brand', 'power_source']
    search_fields = ['inventory_item__name', 'brand', 'model', 'serial_number']
    ordering_fields = ['inventory_item__name', 'brand', 'last_maintenance_date', 'next_maintenance_date']
    
    def get_queryset(self):
        """Return equipment owned by the current user"""
        return Equipment.objects.filter(inventory_item__user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Get equipment due for maintenance",
        responses={200: EquipmentSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def maintenance_due(self, request):
        """Get equipment that is due for maintenance"""
        from django.utils import timezone
        today = timezone.now().date()
        
        equipment = self.get_queryset().filter(next_maintenance_date__lte=today)
        serializer = self.get_serializer(equipment, many=True)
        return Response(serializer.data)


class FarmInputViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing farm inputs.
    
    Farm inputs include seeds, fertilizers, pesticides, and other consumable items.
    """
    serializer_class = FarmInputSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['input_category', 'inventory_item__status']
    search_fields = ['inventory_item__name', 'brand', 'manufacturer', 'batch_number']
    ordering_fields = ['inventory_item__name', 'expiry_date', 'purchase_date']
    
    def get_queryset(self):
        """Return farm inputs owned by the current user"""
        return FarmInput.objects.filter(inventory_item__user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Get expired farm inputs",
        responses={200: FarmInputSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get farm inputs that have expired"""
        from django.utils import timezone
        today = timezone.now().date()
        
        inputs = self.get_queryset().filter(expiry_date__lt=today)
        serializer = self.get_serializer(inputs, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Get farm inputs by category",
        responses={200: FarmInputSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Filter farm inputs by category"""
        category = request.query_params.get('category')
        if not category:
            return Response(
                {"error": "Category parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        inputs = self.get_queryset().filter(input_category=category)
        serializer = self.get_serializer(inputs, many=True)
        return Response(serializer.data)


class InventoryTransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing inventory transactions.
    
    Inventory transactions track movements, usage, and adjustments to inventory items.
    """
    serializer_class = InventoryTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['transaction_type', 'inventory_item', 'related_farm', 'date']
    search_fields = ['inventory_item__name', 'notes']
    ordering_fields = ['date', 'created_at', 'quantity']
    
    def get_queryset(self):
        """Return inventory transactions performed by the current user"""
        return InventoryTransaction.objects.filter(performed_by=self.request.user)
    
    def perform_create(self, serializer):
        """Set the performed_by to the current user when creating a transaction"""
        serializer.save(performed_by=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Get transactions by item",
        responses={200: InventoryTransactionSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_item(self, request):
        """Filter transactions by inventory item"""
        item_id = request.query_params.get('item_id')
        if not item_id:
            return Response(
                {"error": "item_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transactions = self.get_queryset().filter(inventory_item_id=item_id)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing maintenance records.
    
    Maintenance records track service, repairs, and upkeep of equipment.
    """
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['equipment', 'maintenance_type', 'maintenance_date']
    search_fields = ['description', 'parts_replaced', 'service_provider']
    ordering_fields = ['maintenance_date', 'created_at']
    
    def get_queryset(self):
        """Return maintenance records recorded by the current user"""
        return MaintenanceRecord.objects.filter(recorded_by=self.request.user)
    
    def perform_create(self, serializer):
        """Set the recorded_by to the current user when creating a maintenance record"""
        serializer.save(recorded_by=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Get maintenance history for equipment",
        responses={200: MaintenanceRecordSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def equipment_history(self, request):
        """Get maintenance history for a specific equipment"""
        equipment_id = request.query_params.get('equipment_id')
        if not equipment_id:
            return Response(
                {"error": "equipment_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        records = self.get_queryset().filter(equipment_id=equipment_id)
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)
