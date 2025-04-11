from rest_framework import serializers
from .models import InventoryItem, Equipment, FarmInput, InventoryTransaction, MaintenanceRecord

class InventoryItemSerializer(serializers.ModelSerializer):
    """Serializer for general inventory items"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    item_type_display = serializers.CharField(source='get_item_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'user', 'user_name', 'farm', 'farm_name', 'name', 'item_type', 
            'item_type_display', 'description', 'quantity', 'unit', 'status', 
            'status_display', 'storage_location', 'acquisition_date', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class EquipmentSerializer(serializers.ModelSerializer):
    """Serializer for equipment inventory items"""
    inventory_item = InventoryItemSerializer()
    
    class Meta:
        model = Equipment
        fields = [
            'inventory_item', 'brand', 'model', 'serial_number', 'purchase_price',
            'warranty_expiry', 'power_source', 'horsepower', 'last_maintenance_date',
            'next_maintenance_date', 'maintenance_interval_days'
        ]
    
    def create(self, validated_data):
        inventory_item_data = validated_data.pop('inventory_item')
        inventory_item_data['item_type'] = 'equipment'
        inventory_item = InventoryItem.objects.create(**inventory_item_data)
        equipment = Equipment.objects.create(inventory_item=inventory_item, **validated_data)
        return equipment
    
    def update(self, instance, validated_data):
        inventory_item_data = validated_data.pop('inventory_item', None)
        if inventory_item_data:
            inventory_item = instance.inventory_item
            for attr, value in inventory_item_data.items():
                setattr(inventory_item, attr, value)
            inventory_item.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class FarmInputSerializer(serializers.ModelSerializer):
    """Serializer for farm input inventory items"""
    inventory_item = InventoryItemSerializer()
    input_category_display = serializers.CharField(source='get_input_category_display', read_only=True)
    
    class Meta:
        model = FarmInput
        fields = [
            'inventory_item', 'input_category', 'input_category_display', 'brand',
            'manufacturer', 'supplier', 'purchase_date', 'purchase_price',
            'expiry_date', 'batch_number', 'application_rate', 'application_method'
        ]
    
    def create(self, validated_data):
        inventory_item_data = validated_data.pop('inventory_item')
        inventory_item_data['item_type'] = 'input'
        inventory_item = InventoryItem.objects.create(**inventory_item_data)
        farm_input = FarmInput.objects.create(inventory_item=inventory_item, **validated_data)
        return farm_input
    
    def update(self, instance, validated_data):
        inventory_item_data = validated_data.pop('inventory_item', None)
        if inventory_item_data:
            inventory_item = instance.inventory_item
            for attr, value in inventory_item_data.items():
                setattr(inventory_item, attr, value)
            inventory_item.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class InventoryTransactionSerializer(serializers.ModelSerializer):
    """Serializer for inventory transactions"""
    performed_by_name = serializers.CharField(source='performed_by.username', read_only=True)
    inventory_item_name = serializers.CharField(source='inventory_item.name', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'inventory_item', 'inventory_item_name', 'transaction_type', 
            'transaction_type_display', 'quantity', 'date', 'performed_by', 
            'performed_by_name', 'related_farm', 'notes', 'created_at'
        ]
        read_only_fields = ['created_at', 'performed_by']

class MaintenanceRecordSerializer(serializers.ModelSerializer):
    """Serializer for equipment maintenance records"""
    equipment_name = serializers.CharField(source='equipment.inventory_item.name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.username', read_only=True)
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)
    
    class Meta:
        model = MaintenanceRecord
        fields = [
            'id', 'equipment', 'equipment_name', 'maintenance_type', 
            'maintenance_type_display', 'maintenance_date', 'cost', 
            'hours_spent', 'description', 'parts_replaced', 'service_provider',
            'recorded_by', 'recorded_by_name', 'created_at'
        ]
        read_only_fields = ['created_at', 'recorded_by']