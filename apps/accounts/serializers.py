from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import FarmerProfile, SupplierProfile, OfftakerProfile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'user_type', 'phone_number', 'profile_picture', 'date_of_birth',
            'address', 'city', 'state', 'country', 'latitude', 'longitude',
            'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_verified']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user with password handling"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'user_type', 'phone_number'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        # Check that the two passwords match
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return data
    
    def create(self, validated_data):
        # Remove password_confirm from the data
        validated_data.pop('password_confirm')
        
        # Create the user with the validated data
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create the appropriate profile based on user_type
        if user.user_type == User.UserType.FARMER:
            FarmerProfile.objects.create(user=user)
        elif user.user_type == User.UserType.SUPPLIER:
            SupplierProfile.objects.create(user=user, company_name=f"{user.first_name}'s Company")
        elif user.user_type == User.UserType.OFFTAKER:
            OfftakerProfile.objects.create(user=user, company_name=f"{user.first_name}'s Company")
        
        return user

class FarmerProfileSerializer(serializers.ModelSerializer):
    """Serializer for the FarmerProfile model"""
    class Meta:
        model = FarmerProfile
        fields = ['farm_size_hectares', 'years_of_experience', 'primary_crop']

class SupplierProfileSerializer(serializers.ModelSerializer):
    """Serializer for the SupplierProfile model"""
    class Meta:
        model = SupplierProfile
        fields = ['company_name', 'business_registration_number', 'product_categories']

class OfftakerProfileSerializer(serializers.ModelSerializer):
    """Serializer for the OfftakerProfile model"""
    class Meta:
        model = OfftakerProfile
        fields = ['company_name', 'business_registration_number', 'preferred_crops', 'purchase_capacity']

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer that includes the appropriate profile based on user type"""
    farmer_profile = FarmerProfileSerializer(read_only=True)
    supplier_profile = SupplierProfileSerializer(read_only=True)
    offtaker_profile = OfftakerProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'user_type', 'phone_number', 'profile_picture', 'date_of_birth',
            'address', 'city', 'state', 'country', 'latitude', 'longitude',
            'is_verified', 'created_at', 'updated_at',
            'farmer_profile', 'supplier_profile', 'offtaker_profile'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_verified', 'user_type']

class FarmerProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a farmer's profile"""
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    phone_number = serializers.CharField(source='user.phone_number', required=False)
    address = serializers.CharField(source='user.address', required=False)
    city = serializers.CharField(source='user.city', required=False)
    state = serializers.CharField(source='user.state', required=False)
    country = serializers.CharField(source='user.country', required=False)
    
    class Meta:
        model = FarmerProfile
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'address', 'city', 'state', 'country',
            'farm_size_hectares', 'years_of_experience', 'primary_crop'
        ]
    
    def update(self, instance, validated_data):
        # Update User model fields if they exist in validated_data
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        for attr, value in user_data.items():
            setattr(user, attr, value)
        
        user.save()
        
        # Update FarmerProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class SupplierProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a supplier's profile"""
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    phone_number = serializers.CharField(source='user.phone_number', required=False)
    address = serializers.CharField(source='user.address', required=False)
    city = serializers.CharField(source='user.city', required=False)
    state = serializers.CharField(source='user.state', required=False)
    country = serializers.CharField(source='user.country', required=False)
    
    class Meta:
        model = SupplierProfile
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'address', 'city', 'state', 'country',
            'company_name', 'business_registration_number', 'product_categories'
        ]
    
    def update(self, instance, validated_data):
        # Update User model fields if they exist in validated_data
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        for attr, value in user_data.items():
            setattr(user, attr, value)
        
        user.save()
        
        # Update SupplierProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class OfftakerProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating an offtaker's profile"""
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    phone_number = serializers.CharField(source='user.phone_number', required=False)
    address = serializers.CharField(source='user.address', required=False)
    city = serializers.CharField(source='user.city', required=False)
    state = serializers.CharField(source='user.state', required=False)
    country = serializers.CharField(source='user.country', required=False)
    
    class Meta:
        model = OfftakerProfile
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'address', 'city', 'state', 'country',
            'company_name', 'business_registration_number', 'preferred_crops', 'purchase_capacity'
        ]
    
    def update(self, instance, validated_data):
        # Update User model fields if they exist in validated_data
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        for attr, value in user_data.items():
            setattr(user, attr, value)
        
        user.save()
        
        # Update OfftakerProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    
    def validate(self, data):
        # Check that the new passwords match
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "New passwords do not match."})
        return data