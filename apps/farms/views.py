from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.permissions import IsFarmOwner, IsResourceOwner
from .models import Farm, Field, Crop, CropVariety, CropCycle, SoilTest, WeatherRecord
from .serializers import (
    FarmSerializer, FieldSerializer, CropSerializer, 
    CropVarietySerializer, CropCycleSerializer, 
    SoilTestSerializer, WeatherRecordSerializer,
    
)

class FarmViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing farms.
    
    A farm represents a physical farming operation owned by a user.
    Users can create multiple farms and manage them through this API.
    """
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated, IsResourceOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['farm_type', 'city', 'state', 'country']
    search_fields = ['name', 'location', 'city', 'state', 'country']
    ordering_fields = ['name', 'created_at', 'size']
    
    def get_queryset(self):
        """
        This view returns a list of all farms owned by the currently authenticated user.
        """
        return Farm.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        """Set the owner to the current user when creating a farm"""
        serializer.save(owner=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Get summary statistics for a farm",
        responses={
            200: openapi.Response(
                description="Farm statistics retrieved successfully",
                examples={
                    "application/json": {
                        "total_fields": 5,
                        "total_area": 25.5,
                        "area_unit": "hectare",
                        "active_crop_cycles": 3,
                        "total_crops": 8
                    }
                }
            )
        }
    )
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get summary statistics for a farm"""
        farm = self.get_object()
        
        # Get fields for this farm
        fields = Field.objects.filter(farm=farm)
        
        # Get active crop cycles
        active_crop_cycles = CropCycle.objects.filter(
            field__farm=farm,
            status__in=['planned', 'active']
        )
        
        # Get unique crops planted on this farm
        unique_crops = CropCycle.objects.filter(
            field__farm=farm
        ).values_list('crop', flat=True).distinct().count()
        
        # Calculate total area
        total_area = sum(field.size for field in fields)
        
        statistics = {
            'total_fields': fields.count(),
            'total_area': total_area,
            'area_unit': farm.size_unit,
            'active_crop_cycles': active_crop_cycles.count(),
            'total_crops': unique_crops
        }
        
        return Response(statistics)

class FieldViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing fields within a farm.
    
    A field is a subdivision of a farm where crops are grown.
    Fields have properties like size, soil type, and irrigation status.
    """
    serializer_class = FieldSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['farm', 'soil_type', 'is_irrigated']
    search_fields = ['name', 'soil_type']
    ordering_fields = ['name', 'created_at', 'size']
    
    def get_queryset(self):
        """
        This view returns a list of all fields for farms owned by the currently authenticated user.
        """
        return Field.objects.filter(farm__owner=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Get crop history for a field",
        responses={
            200: openapi.Response(
                description="Field crop history retrieved successfully",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "crop_name": "Corn",
                            "start_date": "2023-03-15",
                            "end_date": "2023-07-20",
                            "status": "completed",
                            "yield_amount": 5000,
                            "yield_unit": "kg"
                        }
                    ]
                }
            )
        }
    )
    @action(detail=True, methods=['get'])
    def crop_history(self, request, pk=None):
        """Get crop history for a field"""
        field = self.get_object()
        
        # Get all crop cycles for this field
        crop_cycles = CropCycle.objects.filter(field=field)
        
        # Serialize the data
        serializer = CropCycleSerializer(crop_cycles, many=True)
        
        return Response(serializer.data)

class CropViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing crop types.
    
    Crops represent different plant types that can be grown on a farm.
    This includes information like growing season and days to maturity.
    """
    queryset = Crop.objects.all()
    serializer_class = CropSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['crop_type', 'growing_season']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'days_to_maturity']
    
    @swagger_auto_schema(
        operation_description="Get recommended planting dates for a crop",
        responses={
            200: openapi.Response(
                description="Recommended planting dates retrieved successfully",
                examples={
                    "application/json": {
                        "crop_name": "Tomato",
                        "recommended_seasons": ["spring", "summer"],
                        "planting_windows": [
                            {"region": "North", "start_date": "April 15", "end_date": "May 30"},
                            {"region": "South", "start_date": "March 1", "end_date": "April 15"}
                        ]
                    }
                }
            )
        }
    )
    @action(detail=True, methods=['get'])
    def planting_dates(self, request, pk=None):
        """Get recommended planting dates for a crop"""
        crop = self.get_object()
        
        # This would typically come from a more sophisticated system
        # For now, we'll return some sample data
        planting_data = {
            'crop_name': crop.name,
            'recommended_seasons': [crop.growing_season],
            'planting_windows': [
                {"region": "North", "start_date": "April 15", "end_date": "May 30"},
                {"region": "South", "start_date": "March 1", "end_date": "April 15"}
            ]
        }
        
        return Response(planting_data)

class CropCycleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing crop cycles.
    
    A crop cycle represents the planting, growing, and harvesting of a specific crop
    in a specific field during a specific time period.
    """
    serializer_class = CropCycleSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['field', 'crop', 'status']
    search_fields = ['notes']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    
    # def get_serializer_class(self):
    #     """
    #     Use different serializers for different actions:
    #     - create: CropCycleCreateSerializer
    #     - update/partial_update: CropCycleUpdateSerializer
    #     - others: CropCycleSerializer
    #     """
    #     if self.action == 'create':
    #         return CropCycleCreateSerializer
    #     elif self.action in ['update', 'partial_update']:
    #         return CropCycleUpdateSerializer
    #     return CropCycleSerializer
    
    def get_queryset(self):
        """
        This view returns a list of all crop cycles for fields in farms
        owned by the currently authenticated user.
        """
        return CropCycle.objects.filter(field__farm__owner=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Update the status of a crop cycle",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['status'],
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['planned', 'active', 'completed', 'cancelled'],
                    description='New status for the crop cycle'
                ),
                'notes': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Optional notes about the status change'
                )
            }
        ),
        responses={
            200: CropCycleSerializer
        }
    )
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update the status of a crop cycle"""
        crop_cycle = self.get_object()
        
        # Update status
        status_value = request.data.get('status')
        if not status_value:
            return Response(
                {"status": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate status value
        valid_statuses = [choice[0] for choice in CropCycle.STATUS_CHOICES]
        if status_value not in valid_statuses:
            return Response(
                {"status": [f"Invalid status. Must be one of: {', '.join(valid_statuses)}"]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        crop_cycle.status = status_value
        
        # Update notes if provided
        notes = request.data.get('notes')
        if notes:
            crop_cycle.notes = notes
        
        crop_cycle.save()
        
        serializer = self.get_serializer(crop_cycle)
        return Response(serializer.data)


class CropVarietyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for crop varieties.
    Allows CRUD operations on crop varieties.
    """
    queryset = CropVariety.objects.all()
    serializer_class = CropVarietySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['crop', 'name', 'maturity_days']
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        """Filter queryset to only show varieties for crops owned by the user"""
        if self.request.user.is_staff:
            return CropVariety.objects.all()
        return CropVariety.objects.filter(crop__in=Crop.objects.all())
    
    def perform_create(self, serializer):
        serializer.save()


class SoilTestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for soil tests.
    Allows CRUD operations on soil test records.
    """
    queryset = SoilTest.objects.all()
    serializer_class = SoilTestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['field', 'test_date', 'ph_level']
    
    def get_queryset(self):
        """Filter queryset to only show soil tests for fields owned by the user"""
        if self.request.user.is_staff:
            return SoilTest.objects.all()
        return SoilTest.objects.filter(field__farm__owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save()


class WeatherRecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint for weather records.
    Allows CRUD operations on weather records.
    """
    queryset = WeatherRecord.objects.all()
    serializer_class = WeatherRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['farm', 'record_date', 'temperature', 'precipitation']
    
    def get_queryset(self):
        """Filter queryset to only show weather records for farms owned by the user"""
        if self.request.user.is_staff:
            return WeatherRecord.objects.all()
        return WeatherRecord.objects.filter(farm__owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save()
