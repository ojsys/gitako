from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import InputInventory, ProduceInventory, InventoryTransaction
from .serializers import (
    InputInventorySerializer, ProduceInventorySerializer, InventoryTransactionSerializer
)

class IsFarmOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow farm owners to edit inventory.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the farm owner
        return obj.farm.owner == request.user

class InputInventoryViewSet(viewsets.ModelViewSet):
    """ViewSet for InputInventory model"""
    serializer_class = InputInventorySerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['farm', 'product', 'status', 'purchase_date']
    search_fields = ['product__product__name', 'batch_number', 'storage_location', 'notes']
    ordering_fields = ['purchase_date', 'expiry_date', 'quantity', 'created_at']
    
    def get_queryset(self):
        """
        This view should return a list of all input inventory items
        for farms owned by the currently authenticated user.
        """
        user = self.request.user
        return InputInventory.objects.filter(farm__owner=user)
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Record usage of an input inventory item"""
        inventory = self.get_object()
        
        # Get the quantity to use
        quantity = request.data.get('quantity')
        if not quantity:
            return Response(
                {"quantity": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = float(quantity)
        except ValueError:
            return Response(
                {"quantity": ["Must be a number."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if there's enough quantity
        if quantity > inventory.quantity:
            return Response(
                {"quantity": [f"Not enough inventory. Current quantity: {inventory.quantity}."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the inventory quantity
        inventory.quantity -= quantity
        if inventory.quantity == 0:
            inventory.status = 'depleted'
        inventory.save()
        
        # Create a transaction record
        transaction = InventoryTransaction.objects.create(
            farm=inventory.farm,
            transaction_type='usage',
            input_inventory=inventory,
            quantity=quantity,
            unit=inventory.unit,
            transaction_date=request.data.get('transaction_date'),
            reference_number=request.data.get('reference_number', ''),
            notes=request.data.get('notes', ''),
            updated_by=request.user
        )
        
        return Response({
            'inventory': InputInventorySerializer(inventory).data,
            'transaction': InventoryTransactionSerializer(transaction).data
        })

class ProduceInventoryViewSet(viewsets.ModelViewSet):
    """ViewSet for ProduceInventory model"""
    serializer_class = ProduceInventorySerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['farm', 'product', 'status', 'harvest_date', 'quality_grade']
    search_fields = ['product__product__name', 'batch_number', 'storage_location', 'notes']
    ordering_fields = ['harvest_date', 'storage_date', 'quantity', 'created_at']
    
    def get_queryset(self):
        """
        This view should return a list of all produce inventory items
        for farms owned by the currently authenticated user.
        """
        user = self.request.user
        return ProduceInventory.objects.filter(farm__owner=user)
    
    @action(detail=True, methods=['post'])
    def sell(self, request, pk=None):
        """Record sale of a produce inventory item"""
        inventory = self.get_object()
        
        # Get the quantity to sell
        quantity = request.data.get('quantity')
        if not quantity:
            return Response(
                {"quantity": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = float(quantity)
        except ValueError:
            return Response(
                {"quantity": ["Must be a number."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if there's enough quantity
        if quantity > inventory.quantity:
            return Response(
                {"quantity": [f"Not enough inventory. Current quantity: {inventory.quantity}."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the inventory quantity
        inventory.quantity -= quantity
        if inventory.quantity == 0:
            inventory.status = 'sold_out'
        inventory.save()
        
        # Create a transaction record
        transaction = InventoryTransaction.objects.create(
            farm=inventory.farm,
            transaction_type='sale',
            produce_inventory=inventory,
            quantity=quantity,
            unit=inventory.unit,
            transaction_date=request.data.get('transaction_date'),
            reference_number=request.data.get('reference_number', ''),
            notes=request.data.get('notes', ''),
            updated_by=request.user
        )
        
        return Response({
            'inventory': ProduceInventorySerializer(inventory).data,
            'transaction': InventoryTransactionSerializer(transaction).data
        })

class InventoryTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for InventoryTransaction model"""
    serializer_class = InventoryTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['farm', 'transaction_type', 'transaction_date']
    search_fields = ['reference_number', 'notes']
    ordering_fields = ['transaction_date', 'created_at']
    
    def get_queryset(self):
        """
        This view should return a list of all inventory transactions
        for farms owned by the currently authenticated user.
        """
        user = self.request.user
        return InventoryTransaction.objects.filter(farm__owner=user)
    
    @action(detail=False, methods=['get'])
    def input_transactions(self, request):
        """Get all transactions related to input inventory"""
        queryset = self.get_queryset().filter(input_inventory__isnull=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def produce_transactions(self, request):
        """Get all transactions related to produce inventory"""
        queryset = self.get_queryset().filter(produce_inventory__isnull=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
