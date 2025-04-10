from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the object has an owner field and if the request user is the owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        # Check if the object has a user field and if the request user is that user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if the object has a created_by field and if the request user is the creator
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'admin'

class IsFarmer(permissions.BasePermission):
    """
    Custom permission to only allow farmers to access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'farmer'

class IsSupplier(permissions.BasePermission):
    """
    Custom permission to only allow suppliers to access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'supplier'

class IsOfftaker(permissions.BasePermission):
    """
    Custom permission to only allow off-takers to access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'offtaker'