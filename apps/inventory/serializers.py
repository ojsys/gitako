from rest_framework import serializers
from .models import InputInventory, ProduceInventory, InventoryTransaction

class InputInventorySerializer(serializers.ModelSerializer):
    """Serializer for farm input inventory"""
    product_name = serializers.CharField(source='product.product.name', read_only=True)
    supplier_name = serializers.CharField(source='product.supplier.username', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    
    class Meta:
        model = InputInventory
        fields = [
            'id', 'product', 'product_name', 'supplier_name', 'farm', 'farm_name',
            'quantity', 'unit', 'purchase_date', 'expiry_date', 'batch_number',
            'storage_location', 'status', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class ProduceInventorySerializer(serializers.ModelSerializer):
    """Serializer for farm produce inventory"""
    product_name = serializers.CharField(source='product.product.name', read_only=True)
    crop_name = serializers.CharField(source='product.crop.name', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    
    class Meta:
        model = ProduceInventory
        fields = [
            'id', 'product', 'product_name', 'crop_name', 'farm', 'farm_name',
            'quantity', 'unit', 'harvest_date', 'storage_date', 'batch_number',
            'storage_location', 'status', 'quality_grade', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class InventoryTransactionSerializer(serializers.ModelSerializer):
    """Serializer for inventory transactions"""
    input_product_name = serializers.CharField(source='input_inventory.product.product.name', read_only=True, allow_null=True)
    produce_product_name = serializers.CharField(source='produce_inventory.product.product.name', read_only=True, allow_null=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'farm', 'farm_name', 'transaction_type', 'transaction_type_display',
            'input_inventory', 'input_product_name', 'produce_inventory', 'produce_product_name',
            'quantity', 'unit', 'transaction_date', 'reference_number',
            'notes', 'created_at', 'updated_by'
        ]
        read_only_fields = ['created_at', 'updated_by']
    
    def create(self, validated_data):
        # Set the updated_by to the current user
        validated_data['updated_by'] = self.context['request'].user
        return super().create(validated_data)