from rest_framework import permissions

class IsInventoryManager(permissions.BasePermission):
    """
    Custom permission to only allow inventory managers to access sensitive operations
    """
    def has_permission(self, request, view):
        # Check if user is staff or has specific inventory management role
        return request.user and (request.user.is_staff or request.user.groups.filter(name='Inventory Managers').exists())

class IsOwnerOrInventoryManager(permissions.BasePermission):
    """
    Allow owners to edit their own objects, but inventory managers can edit all
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is inventory manager
        if request.user and (request.user.is_staff or request.user.groups.filter(name='Inventory Managers').exists()):
            return True
        
        # Check if user created the object
        if hasattr(obj, 'created_by') and obj.created_by == request.user:
            return True
        
        if hasattr(obj, 'adjusted_by') and obj.adjusted_by == request.user:
            return True
            
        return False