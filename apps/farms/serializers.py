from rest_framework import serializers
from .models import Farm, Field, Crop, CropVariety, CropCycle, SoilTest, WeatherRecord

class CropSerializer(serializers.ModelSerializer):
    """Serializer for the Crop model"""
    class Meta:
        model = Crop
        fields = '__all__'

class CropVarietySerializer(serializers.ModelSerializer):
    """Serializer for the CropVariety model"""
    crop_name = serializers.CharField(source='crop.name', read_only=True)
    
    class Meta:
        model = CropVariety
        fields = '__all__'

class SoilTestSerializer(serializers.ModelSerializer):
    """Serializer for the SoilTest model"""
    field_name = serializers.CharField(source='field.name', read_only=True)
    
    class Meta:
        model = SoilTest
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class WeatherRecordSerializer(serializers.ModelSerializer):
    """Serializer for the WeatherRecord model"""
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    
    class Meta:
        model = WeatherRecord
        fields = '__all__'
        read_only_fields = ['created_at']

class FieldSerializer(serializers.ModelSerializer):
    """Serializer for the Field model"""
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    soil_tests = SoilTestSerializer(many=True, read_only=True)
    
    class Meta:
        model = Field
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class CropCycleSerializer(serializers.ModelSerializer):
    """Serializer for the CropCycle model"""
    field_name = serializers.CharField(source='field.name', read_only=True)
    crop_name = serializers.CharField(source='crop.name', read_only=True)
    crop_variety_name = serializers.CharField(source='crop_variety.name', read_only=True)
    
    class Meta:
        model = CropCycle
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class FarmSerializer(serializers.ModelSerializer):
    """Serializer for the Farm model"""
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    fields = FieldSerializer(many=True, read_only=True)
    weather_records = WeatherRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = Farm
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'owner']
    
    def create(self, validated_data):
        # Set the owner to the current user
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

class FarmDetailSerializer(FarmSerializer):
    """Detailed serializer for the Farm model including all related data"""
    fields = FieldSerializer(many=True, read_only=True)
    
    class Meta(FarmSerializer.Meta):
        pass