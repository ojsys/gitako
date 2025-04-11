from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import FarmerProfile, SupplierProfile, OfftakerProfile
from .serializers import (
    UserSerializer, FarmerProfileUpdateSerializer, SupplierProfileUpdateSerializer, 
    OfftakerProfileUpdateSerializer, PasswordChangeSerializer, 
    UserRegistrationSerializer, CustomTokenObtainPairSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view that uses our enhanced token serializer."""
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """Instantiates and returns the list of permissions that this view requires."""
        if self.action == 'create' or self.action == 'register':
            permission_classes = [permissions.AllowAny]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]  # We'll refine this with custom permissions
        elif self.action == 'list':
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on the action."""
        if self.action == 'create' or self.action == 'register':
            return UserRegistrationSerializer
        elif self.action == 'change_password':
            return PasswordChangeSerializer
        return UserSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new user with the registration serializer."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Use the standard serializer for the response
        response_serializer = UserSerializer(user)
        
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Alternative registration endpoint."""
        return self.create(request)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request, pk=None):
        """Change user password."""
        user = self.get_object()
        
        # Check if user is trying to change their own password or is admin
        if str(user.id) != str(request.user.id) and not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to change this user's password."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response(
                {"detail": "Password updated successfully"},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get the current user's profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class RegisterView(generics.CreateAPIView):
    """View for user registration"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class FarmerListView(generics.ListAPIView):
    """View to list all farmers"""
    queryset = User.objects.filter(user_type=User.UserType.FARMER)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class SupplierListView(generics.ListAPIView):
    """View to list all suppliers"""
    queryset = User.objects.filter(user_type=User.UserType.SUPPLIER)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class OfftakerListView(generics.ListAPIView):
    """View to list all offtakers"""
    queryset = User.objects.filter(user_type=User.UserType.OFFTAKER)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
