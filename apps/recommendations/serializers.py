from rest_framework import serializers
from .models import Recommendation, RecommendationCategory, RecommendationFeedback

class RecommendationCategorySerializer(serializers.ModelSerializer):
    """Serializer for recommendation categories"""
    class Meta:
        model = RecommendationCategory
        fields = ['id', 'name', 'description', 'icon', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class RecommendationSerializer(serializers.ModelSerializer):
    """Serializer for recommendations"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    field_name = serializers.CharField(source='field.name', read_only=True, allow_null=True)
    crop_cycle_info = serializers.CharField(source='crop_cycle.__str__', read_only=True, allow_null=True)
    
    class Meta:
        model = Recommendation
        fields = [
            'id', 'title', 'description', 'category', 'category_name',
            'farm', 'farm_name', 'field', 'field_name', 'crop_cycle', 'crop_cycle_info',
            'recommendation_type', 'priority', 'status', 'due_date',
            'expected_benefit', 'expected_cost', 'data_source',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class RecommendationFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for recommendation feedback"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    recommendation_title = serializers.CharField(source='recommendation.title', read_only=True)
    
    class Meta:
        model = RecommendationFeedback
        fields = [
            'id', 'recommendation', 'recommendation_title', 'user', 'user_name',
            'is_helpful', 'feedback_text', 'implemented', 'implementation_date',
            'implementation_result', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user']
    
    def create(self, validated_data):
        # Set the user to the current user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)