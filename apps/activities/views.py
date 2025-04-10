from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Activity, ActivityImage, PlantingActivity, FertilizerActivity,
    PestControlActivity, IrrigationActivity, HarvestActivity, ActivityReminder
)
from .serializers import (
    ActivitySerializer, ActivityImageSerializer, PlantingActivitySerializer,
    FertilizerActivitySerializer, PestControlActivitySerializer,
    IrrigationActivitySerializer, HarvestActivitySerializer, ActivityReminderSerializer
)

class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators of an activity to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the creator
        return obj.created_by == request.user

class ActivityViewSet(viewsets.ModelViewSet):
    """ViewSet for Activity model"""
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsCreatorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['field', 'crop_cycle', 'activity_type', 'status', 'planned_date']
    search_fields = ['title', 'description', 'notes']
    ordering_fields = ['planned_date', 'actual_date', 'created_at']
    
    def get_queryset(self):
        """
        This view should return a list of all activities
        for farms owned by the currently authenticated user.
        """
        user = self.request.user
        return Activity.objects.filter(field__farm__owner=user)
    
    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """Upload an image for an activity"""
        activity = self.get_object()
        
        if 'image' not in request.FILES:
            return Response(
                {'image': ['No image provided.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the activity image
        image = ActivityImage.objects.create(
            activity=activity,
            image=request.FILES['image'],
            caption=request.data.get('caption', '')
        )
        
        serializer = ActivityImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark an activity as completed"""
        activity = self.get_object()
        
        # Update the status and actual date
        activity.status = 'completed'
        activity.actual_date = request.data.get('actual_date', None)
        
        # Update other fields if provided
        if 'notes' in request.data:
            activity.notes = request.data['notes']
        
        if 'labor_cost' in request.data:
            activity.labor_cost = request.data['labor_cost']
        
        if 'material_cost' in request.data:
            activity.material_cost = request.data['material_cost']
        
        if 'other_cost' in request.data:
            activity.other_cost = request.data['other_cost']
        
        activity.save()
        
        serializer = self.get_serializer(activity)
        return Response(serializer.data)

class PlantingActivityViewSet(viewsets.ModelViewSet):
    """ViewSet for PlantingActivity model"""
    serializer_class = PlantingActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsCreatorOrReadOnly]
    
    def get_queryset(self):
        """
        This view should return a list of all planting activities
        for farms owned by the currently authenticated user.
        """
        user = self.request.user
        return PlantingActivity.objects.filter(activity__field__farm__owner=user)

class FertilizerActivityViewSet(viewsets.ModelViewSet):
    """ViewSet for FertilizerActivity model"""
    serializer_class = FertilizerActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsCreatorOrReadOnly]
    
    def get_queryset(self):
        """
        This view should return a list of all fertilizer activities
        for farms owned by the currently authenticated user.
        """
        user = self.request.user
        return FertilizerActivity.objects.filter(activity__field__farm__owner=user)

class PestControlActivityViewSet(viewsets.ModelViewSet):
    """ViewSet for PestControlActivity model"""
    serializer_class = PestControlActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsCreatorOrReadOnly]
    
    def get_queryset(self):
        """
        This view should return a list of all pest control activities
        for farms owned by the currently authenticated user.
        """
        user = self.request.user
        return PestControlActivity.objects.filter(activity__field__farm__owner=user)

class IrrigationActivityViewSet(viewsets.ModelViewSet):
    """ViewSet for IrrigationActivity model"""
    serializer_class = IrrigationActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsCreatorOrReadOnly]
    
    def get_queryset(self):
        """
        This view should return a list of all irrigation activities
        for farms owned by the currently authenticated user.
        """
        user = self.request.user
        return IrrigationActivity.objects.filter(activity__field__farm__owner=user)

class HarvestActivityViewSet(viewsets.ModelViewSet):
    """ViewSet for HarvestActivity model"""
    serializer_class = HarvestActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsCreatorOrReadOnly]
    
    def get_queryset(self):
        """
        This view should return a list of all harvest activities
        for farms owned by the currently authenticated user.
        """
        user = self.request.user
        return HarvestActivity.objects.filter(activity__field__farm__owner=user)

class ActivityReminderViewSet(viewsets.ModelViewSet):
    """ViewSet for ActivityReminder model"""
    serializer_class = ActivityReminderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        This view should return a list of all activity reminders
        for activities created by the currently authenticated user.
        """
        user = self.request.user
        return ActivityReminder.objects.filter(activity__created_by=user)
