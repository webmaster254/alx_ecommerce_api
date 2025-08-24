# orders/permissions.py
from rest_framework import permissions

class IsOrderOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an order to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is the owner of the order
        return obj.user == request.user

class IsStaffOrOrderOwner(permissions.BasePermission):
    """
    Custom permission to allow staff users or order owners.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Staff users can access any object
        if request.user.is_staff:
            return True
        
        # For order-related objects, check if user owns the order
        if hasattr(obj, 'order'):
            return obj.order.user == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False