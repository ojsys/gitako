from rest_framework import serializers
from .models import (
    Recommendation, CropRecommendation, RecommendedCrop,
    FertilizerRecommendation, PestControlRecommendation,
    IrrigationRecommendation, MarketRecommendation
)
from apps.farms.models import Crop

class RecommendationSerializer(serializers.ModelSerializer):
    """Serializer for the base Recommendation model"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    field_name = serializers.CharField(source='field.name', read_only=True)
    crop_cycle_name = serializers.CharField(source='crop_cycle.crop.name', read_only=True)
    recommendation_type_display = serializers.CharField(source='get_recommendation_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Recommendation
        fields = [
            'id', 'user', 'user_name', 'farm', 'farm_name', 'field', 'field_name',
            'crop_cycle', 'crop_cycle_name', 'recommendation_type', 'recommendation_type_display',
            'title', 'description', 'priority', 'priority_display', 'status', 'status_display',
            'valid_from', 'valid_until', 'user_feedback', 'user_rating',
            'created_at', 'updated_at', 'is_valid'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_valid']

class RecommendedCropSerializer(serializers.ModelSerializer):
    """Serializer for recommended crops"""
    crop_name = serializers.CharField(source='crop.name', read_only=True)
    crop_category = serializers.CharField(source='crop.category', read_only=True)
    
    class Meta:
        model = RecommendedCrop
        fields = [
            'id', 'crop', 'crop_name', 'crop_category', 'suitability_score',
            'expected_yield', 'expected_profit', 'planting_window_start',
            'planting_window_end', 'notes'
        ]

class CropRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for crop recommendations"""
    recommendation = RecommendationSerializer()
    recommended_crops_detail = RecommendedCropSerializer(source='recommendedcrop_set', many=True, read_only=True)
    recommended_crops_ids = serializers.PrimaryKeyRelatedField(
        source='recommended_crops', queryset=Crop.objects.all(), many=True, write_only=True
    )
    
    class Meta:
        model = CropRecommendation
        fields = [
            'recommendation', 'soil_factors', 'climate_factors', 'market_factors',
            'recommended_crops_detail', 'recommended_crops_ids'
        ]
    
    def create(self, validated_data):
        recommended_crops = validated_data.pop('recommended_crops', [])
        recommendation_data = validated_data.pop('recommendation')
        recommendation_data['recommendation_type'] = 'crop'
        recommendation_data['user'] = self.context['request'].user
        
        # Create the recommendation
        recommendation = Recommendation.objects.create(**recommendation_data)
        
        # Create the crop recommendation
        crop_recommendation = CropRecommendation.objects.create(
            recommendation=recommendation, **validated_data
        )
        
        # Add the recommended crops
        for crop in recommended_crops:
            RecommendedCrop.objects.create(
                crop_recommendation=crop_recommendation,
                crop=crop,
                suitability_score=0  # Default value, would be set properly in a real app
            )
        
        return crop_recommendation
    
    def update(self, instance, validated_data):
        recommendation_data = validated_data.pop('recommendation', None)
        recommended_crops = validated_data.pop('recommended_crops', None)
        
        # Update the recommendation
        if recommendation_data:
            recommendation = instance.recommendation
            for attr, value in recommendation_data.items():
                setattr(recommendation, attr, value)
            recommendation.save()
        
        # Update the crop recommendation fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update recommended crops if provided
        if recommended_crops is not None:
            instance.recommended_crops.clear()
            for crop in recommended_crops:
                RecommendedCrop.objects.create(
                    crop_recommendation=instance,
                    crop=crop,
                    suitability_score=0  # Default value, would be set properly in a real app
                )
        
        return instance

class FertilizerRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for fertilizer recommendations"""
    recommendation = RecommendationSerializer()
    
    class Meta:
        model = FertilizerRecommendation
        fields = [
            'recommendation', 'nitrogen_kg_per_ha', 'phosphorus_kg_per_ha',
            'potassium_kg_per_ha', 'recommended_products', 'application_timing',
            'application_method', 'soil_test_based', 'crop_requirement_based'
        ]
    
    def create(self, validated_data):
        recommendation_data = validated_data.pop('recommendation')
        recommendation_data['recommendation_type'] = 'fertilizer'
        recommendation_data['user'] = self.context['request'].user
        
        # Create the recommendation
        recommendation = Recommendation.objects.create(**recommendation_data)
        
        # Create the fertilizer recommendation
        fertilizer_recommendation = FertilizerRecommendation.objects.create(
            recommendation=recommendation, **validated_data
        )
        
        return fertilizer_recommendation
    
    def update(self, instance, validated_data):
        recommendation_data = validated_data.pop('recommendation', None)
        
        # Update the recommendation
        if recommendation_data:
            recommendation = instance.recommendation
            for attr, value in recommendation_data.items():
                setattr(recommendation, attr, value)
            recommendation.save()
        
        # Update the fertilizer recommendation fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance

class PestControlRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for pest control recommendations"""
    recommendation = RecommendationSerializer()
    
    class Meta:
        model = PestControlRecommendation
        fields = [
            'recommendation', 'target_pest', 'pest_pressure', 'recommended_products',
            'application_timing', 'application_method', 'cultural_controls',
            'biological_controls', 'preventive_measures'
        ]
    
    def create(self, validated_data):
        recommendation_data = validated_data.pop('recommendation')
        recommendation_data['recommendation_type'] = 'pest_control'
        recommendation_data['user'] = self.context['request'].user
        
        # Create the recommendation
        recommendation = Recommendation.objects.create(**recommendation_data)
        
        # Create the pest control recommendation
        pest_control_recommendation = PestControlRecommendation.objects.create(
            recommendation=recommendation, **validated_data
        )
        
        return pest_control_recommendation
    
    def update(self, instance, validated_data):
        recommendation_data = validated_data.pop('recommendation', None)
        
        # Update the recommendation
        if recommendation_data:
            recommendation = instance.recommendation
            for attr, value in recommendation_data.items():
                setattr(recommendation, attr, value)
            recommendation.save()
        
        # Update the pest control recommendation fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance

class IrrigationRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for irrigation recommendations"""
    recommendation = RecommendationSerializer()
    
    class Meta:
        model = IrrigationRecommendation
        fields = [
            'recommendation', 'water_requirement_mm', 'frequency_days',
            'recommended_method', 'irrigation_duration', 'soil_moisture',
            'weather_forecast', 'crop_stage'
        ]
    
    def create(self, validated_data):
        recommendation_data = validated_data.pop('recommendation')
        recommendation_data['recommendation_type'] = 'irrigation'
        recommendation_data['user'] = self.context['request'].user
        
        # Create the recommendation
        recommendation = Recommendation.objects.create(**recommendation_data)
        
        # Create the irrigation recommendation
        irrigation_recommendation = IrrigationRecommendation.objects.create(
            recommendation=recommendation, **validated_data
        )
        
        return irrigation_recommendation
    
    def update(self, instance, validated_data):
        recommendation_data = validated_data.pop('recommendation', None)
        
        # Update the recommendation
        if recommendation_data:
            recommendation = instance.recommendation
            for attr, value in recommendation_data.items():
                setattr(recommendation, attr, value)
            recommendation.save()
        
        # Update the irrigation recommendation fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance

class MarketRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for market recommendations"""
    recommendation = RecommendationSerializer()
    
    class Meta:
        model = MarketRecommendation
        fields = [
            'recommendation', 'market_trends', 'price_forecast',
            'recommended_timing', 'recommended_markets', 'potential_buyers',
            'current_price_range', 'expected_price_range'
        ]
    
    def create(self, validated_data):
        recommendation_data = validated_data.pop('recommendation')
        recommendation_data['recommendation_type'] = 'market'
        recommendation_data['user'] = self.context['request'].user
        
        # Create the recommendation
        recommendation = Recommendation.objects.create(**recommendation_data)
        
        # Create the market recommendation
        market_recommendation = MarketRecommendation.objects.create(
            recommendation=recommendation, **validated_data
        )
        
        return market_recommendation
    
    def update(self, instance, validated_data):
        recommendation_data = validated_data.pop('recommendation', None)
        
        # Update the recommendation
        if recommendation_data:
            recommendation = instance.recommendation
            for attr, value in recommendation_data.items():
                setattr(recommendation, attr, value)
            recommendation.save()
        
        # Update the market recommendation fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance