from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from api.throttling import RecommendationsThrottle
from .models import Recommendation, RecommendationCategory, RecommendationFeedback
from .serializers import (
    RecommendationSerializer, RecommendationCategorySerializer,
    RecommendationFeedbackSerializer
)

class IsFarmOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow farm owners to edit recommendations.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the farm owner
        if hasattr(obj, 'farm'):
            return obj.farm.owner == request.user
        
        return False

class RecommendationCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for RecommendationCategory model (read-only)"""
    queryset = RecommendationCategory.objects.all()
    serializer_class = RecommendationCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

class RecommendationViewSet(viewsets.ModelViewSet):
    """ViewSet for Recommendation model"""
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['farm', 'field', 'crop_cycle', 'category', 'recommendation_type', 'priority', 'status']
    search_fields = ['title', 'description', 'expected_benefit']
    ordering_fields = ['priority', 'due_date', 'created_at']
    
    def get_queryset(self):
        """
        This view should return a list of all recommendations
        for farms owned by the currently authenticated user.
        """
        user = self.request.user
        return Recommendation.objects.filter(farm__owner=user)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update the status of a recommendation"""
        recommendation = self.get_object()
        
        # Update the status
        status_value = request.data.get('status')
        if not status_value:
            return Response(
                {"status": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recommendation.status = status_value
        recommendation.save()
        
        serializer = self.get_serializer(recommendation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def provide_feedback(self, request, pk=None):
        """Provide feedback for a recommendation"""
        recommendation = self.get_object()
        
        # Create feedback
        feedback_data = {
            'recommendation': recommendation.id,
            'is_helpful': request.data.get('is_helpful', True),
            'feedback_text': request.data.get('feedback_text', ''),
            'implemented': request.data.get('implemented', False),
            'implementation_date': request.data.get('implementation_date', None),
            'implementation_result': request.data.get('implementation_result', '')
        }
        
        serializer = RecommendationFeedbackSerializer(
            data=feedback_data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class RecommendationFeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for RecommendationFeedback model"""
    serializer_class = RecommendationFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['recommendation', 'is_helpful', 'implemented']
    search_fields = ['feedback_text', 'implementation_result']
    ordering_fields = ['created_at', 'implementation_date']
    
    def get_queryset(self):
        """
        This view should return a list of all feedback
        for recommendations associated with farms owned by the currently authenticated user.
        """
        user = self.request.user
        return RecommendationFeedback.objects.filter(recommendation__farm__owner=user)
    
    @action(detail=False, methods=['get'])
    def my_feedback(self, request):
        """Get all feedback provided by the current user"""
        queryset = RecommendationFeedback.objects.filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
