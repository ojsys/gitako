from rest_framework import permissions

class IsFarmer(permissions.BasePermission):
    """
    Custom permission to only allow farmers to access a view.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'farmer'

class IsSupplier(permissions.BasePermission):
    """
    Custom permission to only allow suppliers to access a view.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'supplier'

class IsBuyer(permissions.BasePermission):
    """
    Custom permission to only allow buyers to access a view.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'buyer'

class IsAdvisor(permissions.BasePermission):
    """
    Custom permission to only allow advisors to access a view.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'advisor'

class IsFarmOwner(permissions.BasePermission):
    """
    Custom permission to only allow farm owners to access a view.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the object has a farm attribute
        if hasattr(obj, 'farm'):
            return obj.farm.owner == request.user
        
        # Check if the object is a farm
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False

class IsResourceOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a resource to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the object has a user, owner, created_by, or supplier attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        if hasattr(obj, 'supplier'):
            return obj.supplier == request.user
        
        if hasattr(obj, 'farmer'):
            return obj.farmer == request.user
        
        return False