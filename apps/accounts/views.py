from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import FarmerProfile, SupplierProfile, OfftakerProfile
from .serializers import (
    UserSerializer, UserCreateSerializer, UserProfileSerializer,
    FarmerProfileUpdateSerializer, SupplierProfileUpdateSerializer, 
    OfftakerProfileUpdateSerializer, PasswordChangeSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model"""
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'profile':
            return UserProfileSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'create' or self.action == 'login':
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get the profile of the currently authenticated user"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update the profile of the currently authenticated user"""
        user = request.user
        
        # Select the appropriate serializer based on user type
        if user.user_type == User.UserType.FARMER:
            profile = user.farmer_profile
            serializer = FarmerProfileUpdateSerializer(profile, data=request.data, partial=True)
        elif user.user_type == User.UserType.SUPPLIER:
            profile = user.supplier_profile
            serializer = SupplierProfileUpdateSerializer(profile, data=request.data, partial=True)
        elif user.user_type == User.UserType.OFFTAKER:
            profile = user.offtaker_profile
            serializer = OfftakerProfileUpdateSerializer(profile, data=request.data, partial=True)
        else:
            # For admin users or other types without specific profiles
            serializer = UserSerializer(user, data=request.data, partial=True)
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return the full user profile
        return Response(UserProfileSerializer(user).data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change the password of the currently authenticated user"""
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        # Check if the old password is correct
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': ['Wrong password.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set the new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'status': 'password changed'})
    
    @action(detail=False, methods=['post'])
    def upload_profile_picture(self, request):
        """Upload a profile picture for the currently authenticated user"""
        if 'profile_picture' not in request.FILES:
            return Response(
                {'profile_picture': ['No image provided.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        user.profile_picture = request.FILES['profile_picture']
        user.save()
        
        return Response(UserSerializer(user).data)

class RegisterView(generics.CreateAPIView):
    """View for user registration"""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]

class FarmerListView(generics.ListAPIView):
    """View to list all farmers"""
    queryset = User.objects.filter(user_type=User.UserType.FARMER)
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

class SupplierListView(generics.ListAPIView):
    """View to list all suppliers"""
    queryset = User.objects.filter(user_type=User.UserType.SUPPLIER)
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

class OfftakerListView(generics.ListAPIView):
    """View to list all offtakers"""
    queryset = User.objects.filter(user_type=User.UserType.OFFTAKER)
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
