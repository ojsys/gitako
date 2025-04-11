from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import FarmerProfile, SupplierProfile, OfftakerProfile

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer that includes user data in the token response."""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['user_type'] = user.user_type
        token['is_verified'] = user.is_verified
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add extra responses
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['user_type'] = self.user.user_type
        data['is_verified'] = self.user.is_verified
        
        return data


class FarmerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerProfile
        fields = ['farm_size_hectares', 'years_of_experience', 'primary_crop']


class SupplierProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierProfile
        fields = ['company_name', 'business_registration_number', 'product_categories']


class OfftakerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfftakerProfile
        fields = ['company_name', 'business_registration_number', 'preferred_crops', 'purchase_capacity']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with conditional profile fields based on user_type."""
    farmer_profile = FarmerProfileSerializer(required=False)
    supplier_profile = SupplierProfileSerializer(required=False)
    offtaker_profile = OfftakerProfileSerializer(required=False)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 
                  'user_type', 'phone_number', 'profile_picture', 'date_of_birth',
                  'address', 'city', 'state', 'country', 'latitude', 'longitude',
                  'is_verified', 'created_at', 'updated_at', 'farmer_profile',
                  'supplier_profile', 'offtaker_profile')
        read_only_fields = ('id', 'created_at', 'updated_at', 'is_verified')
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        # Extract profile data based on user_type
        farmer_profile_data = validated_data.pop('farmer_profile', None)
        supplier_profile_data = validated_data.pop('supplier_profile', None)
        offtaker_profile_data = validated_data.pop('offtaker_profile', None)
        
        # Extract password
        password = validated_data.pop('password', None)
        
        # Create user
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        
        # Create appropriate profile based on user_type
        if user.user_type == User.UserType.FARMER and farmer_profile_data:
            FarmerProfile.objects.create(user=user, **farmer_profile_data)
        elif user.user_type == User.UserType.SUPPLIER and supplier_profile_data:
            SupplierProfile.objects.create(user=user, **supplier_profile_data)
        elif user.user_type == User.UserType.OFFTAKER and offtaker_profile_data:
            OfftakerProfile.objects.create(user=user, **offtaker_profile_data)
        
        return user
    
    def update(self, instance, validated_data):
        # Extract profile data based on user_type
        farmer_profile_data = validated_data.pop('farmer_profile', None)
        supplier_profile_data = validated_data.pop('supplier_profile', None)
        offtaker_profile_data = validated_data.pop('offtaker_profile', None)
        
        # Extract password
        password = validated_data.pop('password', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update password if provided
        if password:
            instance.set_password(password)
        
        instance.save()
        
        # Update appropriate profile based on user_type
        if instance.user_type == User.UserType.FARMER and farmer_profile_data:
            farmer_profile, created = FarmerProfile.objects.get_or_create(user=instance)
            for attr, value in farmer_profile_data.items():
                setattr(farmer_profile, attr, value)
            farmer_profile.save()
        
        elif instance.user_type == User.UserType.SUPPLIER and supplier_profile_data:
            supplier_profile, created = SupplierProfile.objects.get_or_create(user=instance)
            for attr, value in supplier_profile_data.items():
                setattr(supplier_profile, attr, value)
            supplier_profile.save()
        
        elif instance.user_type == User.UserType.OFFTAKER and offtaker_profile_data:
            offtaker_profile, created = OfftakerProfile.objects.get_or_create(user=instance)
            for attr, value in offtaker_profile_data.items():
                setattr(offtaker_profile, attr, value)
            offtaker_profile.save()
        
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with profile data."""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    farmer_profile = FarmerProfileSerializer(required=False)
    supplier_profile = SupplierProfileSerializer(required=False)
    offtaker_profile = OfftakerProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 
                  'last_name', 'user_type', 'phone_number', 'farmer_profile', 
                  'supplier_profile', 'offtaker_profile')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Validate that the appropriate profile is provided based on user_type
        user_type = attrs.get('user_type')
        if user_type == User.UserType.FARMER and not attrs.get('farmer_profile'):
            raise serializers.ValidationError({"farmer_profile": "Farmer profile is required for farmer users."})
        elif user_type == User.UserType.SUPPLIER and not attrs.get('supplier_profile'):
            raise serializers.ValidationError({"supplier_profile": "Supplier profile is required for supplier users."})
        elif user_type == User.UserType.OFFTAKER and not attrs.get('offtaker_profile'):
            raise serializers.ValidationError({"offtaker_profile": "Offtaker profile is required for offtaker users."})
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return UserSerializer().create(validated_data)


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs


# Update Serializers
class FarmerProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating farmer profiles."""
    
    class Meta:
        model = FarmerProfile
        exclude = ['user']


class SupplierProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating supplier profiles."""
    
    class Meta:
        model = SupplierProfile
        exclude = ['user']


class OfftakerProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating offtaker profiles."""
    
    class Meta:
        model = OfftakerProfile
        exclude = ['user']