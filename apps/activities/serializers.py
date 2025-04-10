from rest_framework import serializers
from .models import (
    Activity, ActivityImage, PlantingActivity, FertilizerActivity,
    PestControlActivity, IrrigationActivity, HarvestActivity, ActivityReminder
)
from apps.farms.serializers import FieldSerializer, CropCycleSerializer

class ActivityImageSerializer(serializers.ModelSerializer):
    """Serializer for activity images"""
    class Meta:
        model = ActivityImage
        fields = ['id', 'image', 'caption', 'uploaded_at']
        read_only_fields = ['uploaded_at']

class ActivitySerializer(serializers.ModelSerializer):
    """Base serializer for activities"""
    field_name = serializers.CharField(source='field.name', read_only=True)
    crop_cycle_info = serializers.CharField(source='crop_cycle.__str__', read_only=True)
    images = ActivityImageSerializer(many=True, read_only=True)
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Activity
        fields = [
            'id', 'field', 'field_name', 'crop_cycle', 'crop_cycle_info',
            'activity_type', 'activity_type_display', 'planned_date', 'actual_date',
            'status', 'status_display', 'title', 'description', 'notes',
            'labor_cost', 'material_cost', 'other_cost', 'total_cost',
            'temperature', 'humidity', 'weather_notes',
            'created_at', 'updated_at', 'created_by', 'images'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'total_cost']
    
    def create(self, validated_data):
        # Set the created_by to the current user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class PlantingActivitySerializer(serializers.ModelSerializer):
    """Serializer for planting activities"""
    activity = ActivitySerializer()
    
    class Meta:
        model = PlantingActivity
        fields = [
            'activity', 'seed_quantity', 'seed_unit',
            'planting_method', 'spacing'
        ]
    
    def create(self, validated_data):
        activity_data = validated_data.pop('activity')
        activity_data['activity_type'] = 'planting'
        
        # Create the activity
        activity = Activity.objects.create(**activity_data)
        
        # Create the planting activity
        planting_activity = PlantingActivity.objects.create(activity=activity, **validated_data)
        return planting_activity

class FertilizerActivitySerializer(serializers.ModelSerializer):
    """Serializer for fertilizer application activities"""
    activity = ActivitySerializer()
    
    class Meta:
        model = FertilizerActivity
        fields = [
            'activity', 'fertilizer_type', 'application_method',
            'quantity', 'unit'
        ]
    
    def create(self, validated_data):
        activity_data = validated_data.pop('activity')
        activity_data['activity_type'] = 'fertilizer'
        
        # Create the activity
        activity = Activity.objects.create(**activity_data)
        
        # Create the fertilizer activity
        fertilizer_activity = FertilizerActivity.objects.create(activity=activity, **validated_data)
        return fertilizer_activity

class PestControlActivitySerializer(serializers.ModelSerializer):
    """Serializer for pest control activities"""
    activity = ActivitySerializer()
    
    class Meta:
        model = PestControlActivity
        fields = [
            'activity', 'product_name', 'target_pest',
            'application_method', 'quantity', 'unit'
        ]
    
    def create(self, validated_data):
        activity_data = validated_data.pop('activity')
        activity_data['activity_type'] = 'pest_control'
        
        # Create the activity
        activity = Activity.objects.create(**activity_data)
        
        # Create the pest control activity
        pest_control_activity = PestControlActivity.objects.create(activity=activity, **validated_data)
        return pest_control_activity

class IrrigationActivitySerializer(serializers.ModelSerializer):
    """Serializer for irrigation activities"""
    activity = ActivitySerializer()
    
    class Meta:
        model = IrrigationActivity
        fields = [
            'activity', 'irrigation_method', 'water_source',
            'duration_hours', 'water_quantity', 'water_unit'
        ]
    
    def create(self, validated_data):
        activity_data = validated_data.pop('activity')
        activity_data['activity_type'] = 'irrigation'
        
        # Create the activity
        activity = Activity.objects.create(**activity_data)
        
        # Create the irrigation activity
        irrigation_activity = IrrigationActivity.objects.create(activity=activity, **validated_data)
        return irrigation_activity

class HarvestActivitySerializer(serializers.ModelSerializer):
    """Serializer for harvest activities"""
    activity = ActivitySerializer()
    
    class Meta:
        model = HarvestActivity
        fields = [
            'activity', 'yield_quantity', 'yield_unit',
            'quality_grade', 'moisture_content'
        ]
    
    def create(self, validated_data):
        activity_data = validated_data.pop('activity')
        activity_data['activity_type'] = 'harvesting'
        
        # Create the activity
        activity = Activity.objects.create(**activity_data)
        
        # Create the harvest activity
        harvest_activity = HarvestActivity.objects.create(activity=activity, **validated_data)
        return harvest_activity

class ActivityReminderSerializer(serializers.ModelSerializer):
    """Serializer for activity reminders"""
    activity_title = serializers.CharField(source='activity.title', read_only=True)
    
    class Meta:
        model = ActivityReminder
        fields = [
            'id', 'activity', 'activity_title', 'reminder_date', 'reminder_time',
            'send_email', 'send_sms', 'send_push', 'is_sent', 'sent_at', 'created_at'
        ]
        read_only_fields = ['is_sent', 'sent_at', 'created_at']