from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import (
    Recommendation, CropRecommendation, RecommendedCrop,
    FertilizerRecommendation, PestControlRecommendation,
    IrrigationRecommendation, MarketRecommendation
)
from .serializers import (
    RecommendationSerializer, CropRecommendationSerializer, RecommendedCropSerializer,
    FertilizerRecommendationSerializer, PestControlRecommendationSerializer,
    IrrigationRecommendationSerializer, MarketRecommendationSerializer
)
from api.permissions import IsFarmOwner

class RecommendationViewSet(viewsets.ModelViewSet):
    """ViewSet for the base Recommendation model"""
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['farm', 'field', 'crop_cycle', 'recommendation_type', 'priority', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'valid_from', 'valid_until', 'priority']
    
    def get_queryset(self):
        """
        This view returns a list of all recommendations
        for the currently authenticated user.
        """
        return Recommendation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating a recommendation"""
        serializer.save(user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Get active recommendations",
        responses={200: RecommendationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active recommendations"""
        active_recommendations = self.get_queryset().filter(status='active', is_valid=True)
        serializer = self.get_serializer(active_recommendations, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Get recommendations by farm",
        manual_parameters=[
            openapi.Parameter('farm_id', openapi.IN_QUERY, description="Farm ID", type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={200: RecommendationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_farm(self, request):
        """Get recommendations for a specific farm"""
        farm_id = request.query_params.get('farm_id')
        if not farm_id:
            return Response(
                {"error": "farm_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        farm_recommendations = self.get_queryset().filter(farm_id=farm_id)
        serializer = self.get_serializer(farm_recommendations, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Get recommendations by crop cycle",
        manual_parameters=[
            openapi.Parameter('crop_cycle_id', openapi.IN_QUERY, description="Crop Cycle ID", type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={200: RecommendationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_crop_cycle(self, request):
        """Get recommendations for a specific crop cycle"""
        crop_cycle_id = request.query_params.get('crop_cycle_id')
        if not crop_cycle_id:
            return Response(
                {"error": "crop_cycle_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cycle_recommendations = self.get_queryset().filter(crop_cycle_id=crop_cycle_id)
        serializer = self.get_serializer(cycle_recommendations, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Update recommendation status",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['status'],
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['pending', 'active', 'completed', 'rejected'],
                    description='New status for the recommendation'
                ),
                'user_feedback': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User feedback on the recommendation'
                ),
                'user_rating': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='User rating (1-5)'
                )
            }
        ),
        responses={200: RecommendationSerializer()}
    )
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update the status of a recommendation"""
        recommendation = self.get_object()
        
        status_value = request.data.get('status')
        if status_value:
            recommendation.status = status_value
        
        user_feedback = request.data.get('user_feedback')
        if user_feedback:
            recommendation.user_feedback = user_feedback
        
        user_rating = request.data.get('user_rating')
        if user_rating:
            recommendation.user_rating = user_rating
        
        recommendation.save()
        serializer = self.get_serializer(recommendation)
        return Response(serializer.data)

class CropRecommendationViewSet(viewsets.ModelViewSet):
    """ViewSet for crop recommendations"""
    serializer_class = CropRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['recommendation__farm', 'recommendation__field', 'recommendation__crop_cycle']
    search_fields = ['recommendation__title', 'recommendation__description', 'soil_factors', 'climate_factors']
    ordering_fields = ['recommendation__created_at', 'recommendation__valid_from']
    
    def get_queryset(self):
        """
        This view returns a list of all crop recommendations
        for the currently authenticated user.
        """
        return CropRecommendation.objects.filter(recommendation__user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Get recommended crops for a field",
        manual_parameters=[
            openapi.Parameter('field_id', openapi.IN_QUERY, description="Field ID", type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={200: CropRecommendationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def for_field(self, request):
        """Get crop recommendations for a specific field"""
        field_id = request.query_params.get('field_id')
        if not field_id:
            return Response(
                {"error": "field_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        field_recommendations = self.get_queryset().filter(recommendation__field_id=field_id)
        serializer = self.get_serializer(field_recommendations, many=True)
        return Response(serializer.data)

class RecommendedCropViewSet(viewsets.ModelViewSet):
    """ViewSet for recommended crops"""
    serializer_class = RecommendedCropSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['crop_recommendation', 'crop']
    ordering_fields = ['suitability_score', 'expected_profit']
    
    def get_queryset(self):
        """
        This view returns a list of all recommended crops
        for the currently authenticated user.
        """
        return RecommendedCrop.objects.filter(
            crop_recommendation__recommendation__user=self.request.user
        )
    
    @swagger_auto_schema(
        operation_description="Get top recommended crops",
        manual_parameters=[
            openapi.Parameter('limit', openapi.IN_QUERY, description="Number of crops to return", type=openapi.TYPE_INTEGER),
        ],
        responses={200: RecommendedCropSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def top_recommendations(self, request):
        """Get top recommended crops by suitability score"""
        limit = request.query_params.get('limit', 5)
        try:
            limit = int(limit)
        except ValueError:
            limit = 5
        
        top_crops = self.get_queryset().order_by('-suitability_score')[:limit]
        serializer = self.get_serializer(top_crops, many=True)
        return Response(serializer.data)

class FertilizerRecommendationViewSet(viewsets.ModelViewSet):
    """ViewSet for fertilizer recommendations"""
    serializer_class = FertilizerRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['recommendation__farm', 'recommendation__field', 'recommendation__crop_cycle']
    search_fields = ['recommendation__title', 'recommendation__description', 'recommended_products']
    ordering_fields = ['recommendation__created_at', 'recommendation__valid_from']
    
    def get_queryset(self):
        """
        This view returns a list of all fertilizer recommendations
        for the currently authenticated user.
        """
        return FertilizerRecommendation.objects.filter(recommendation__user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Get fertilizer recommendations for a crop cycle",
        manual_parameters=[
            openapi.Parameter('crop_cycle_id', openapi.IN_QUERY, description="Crop Cycle ID", type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={200: FertilizerRecommendationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def for_crop_cycle(self, request):
        """Get fertilizer recommendations for a specific crop cycle"""
        crop_cycle_id = request.query_params.get('crop_cycle_id')
        if not crop_cycle_id:
            return Response(
                {"error": "crop_cycle_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cycle_recommendations = self.get_queryset().filter(recommendation__crop_cycle_id=crop_cycle_id)
        serializer = self.get_serializer(cycle_recommendations, many=True)
        return Response(serializer.data)

class PestControlRecommendationViewSet(viewsets.ModelViewSet):
    """ViewSet for pest control recommendations"""
    serializer_class = PestControlRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['recommendation__farm', 'recommendation__field', 'recommendation__crop_cycle']
    search_fields = ['recommendation__title', 'recommendation__description', 'target_pest', 'recommended_products']
    ordering_fields = ['recommendation__created_at', 'recommendation__valid_from']
    
    def get_queryset(self):
        """
        This view returns a list of all pest control recommendations
        for the currently authenticated user.
        """
        return PestControlRecommendation.objects.filter(recommendation__user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Get pest control recommendations by pest",
        manual_parameters=[
            openapi.Parameter('pest', openapi.IN_QUERY, description="Target pest", type=openapi.TYPE_STRING, required=True),
        ],
        responses={200: PestControlRecommendationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_pest(self, request):
        """Get pest control recommendations for a specific pest"""
        pest = request.query_params.get('pest')
        if not pest:
            return Response(
                {"error": "pest parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pest_recommendations = self.get_queryset().filter(target_pest__icontains=pest)
        serializer = self.get_serializer(pest_recommendations, many=True)
        return Response(serializer.data)

class IrrigationRecommendationViewSet(viewsets.ModelViewSet):
    """ViewSet for irrigation recommendations"""
    serializer_class = IrrigationRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['recommendation__farm', 'recommendation__field', 'recommendation__crop_cycle']
    search_fields = ['recommendation__title', 'recommendation__description', 'recommended_method']
    ordering_fields = ['recommendation__created_at', 'recommendation__valid_from']
    
    def get_queryset(self):
        """
        This view returns a list of all irrigation recommendations
        for the currently authenticated user.
        """
        return IrrigationRecommendation.objects.filter(recommendation__user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Get irrigation recommendations by method",
        manual_parameters=[
            openapi.Parameter('method', openapi.IN_QUERY, description="Irrigation method", type=openapi.TYPE_STRING, required=True),
        ],
        responses={200: IrrigationRecommendationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_method(self, request):
        """Get irrigation recommendations for a specific method"""
        method = request.query_params.get('method')
        if not method:
            return Response(
                {"error": "method parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        method_recommendations = self.get_queryset().filter(recommended_method__icontains=method)
        serializer = self.get_serializer(method_recommendations, many=True)
        return Response(serializer.data)

class MarketRecommendationViewSet(viewsets.ModelViewSet):
    """ViewSet for market recommendations"""
    serializer_class = MarketRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['recommendation__farm', 'recommendation__field', 'recommendation__crop_cycle']
    search_fields = ['recommendation__title', 'recommendation__description', 'market_trends', 'recommended_markets']
    ordering_fields = ['recommendation__created_at', 'recommendation__valid_from']
    
    def get_queryset(self):
        """
        This view returns a list of all market recommendations
        for the currently authenticated user.
        """
        return MarketRecommendation.objects.filter(recommendation__user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Get market recommendations by price range",
        manual_parameters=[
            openapi.Parameter('min_price', openapi.IN_QUERY, description="Minimum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter('max_price', openapi.IN_QUERY, description="Maximum price", type=openapi.TYPE_NUMBER),
        ],
        responses={200: MarketRecommendationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_price_range(self, request):
        """Get market recommendations within a price range"""
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        
        queryset = self.get_queryset()
        
        if min_price:
            try:
                min_price = float(min_price)
                queryset = queryset.filter(current_price_range__gte=min_price)
            except ValueError:
                pass
        
        if max_price:
            try:
                max_price = float(max_price)
                queryset = queryset.filter(current_price_range__lte=max_price)
            except ValueError:
                pass
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
