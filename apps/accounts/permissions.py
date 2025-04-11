from rest_framework import permissions
from .models import User

class IsAdminUser(permissions.BasePermission):
    """Permission to only allow admin users."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == User.UserType.ADMIN


class IsFarmerUser(permissions.BasePermission):
    """Permission to only allow farmer users."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == User.UserType.FARMER


class IsSupplierUser(permissions.BasePermission):
    """Permission to only allow supplier users."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == User.UserType.SUPPLIER


class IsOfftakerUser(permissions.BasePermission):
    """Permission to only allow offtaker users."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == User.UserType.OFFTAKER


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission to only allow owners of an object or admin users."""
    def has_object_permission(self, request, view, obj):
        # Admin permissions
        if request.user.user_type == User.UserType.ADMIN:
            return True
        
        # Instance must have an attribute named `user` or be the user itself
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return obj == request.user