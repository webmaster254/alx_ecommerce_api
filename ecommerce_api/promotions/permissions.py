from rest_framework import permissions

class IsPromotionManager(permissions.BasePermission):
    """Custom permission to only allow promotion managers"""
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or 
                               request.user.groups.filter(name='Promotion Managers').exists())

class CanUsePromotion(permissions.BasePermission):
    """Check if user can use promotion based on usage limits"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # For coupon validation endpoint
        if view.action == 'validate_coupon':
            return True
            
        return IsPromotionManager().has_permission(request, view)