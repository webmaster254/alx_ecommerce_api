from rest_framework import permissions

class IsCartOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a cart to access it.
    Handles both Cart and CartItem objects.
    """
    def has_object_permission(self, request, view, obj):
        # Handle CartItem objects - check through cart relationship
        if hasattr(obj, 'cart'):
            cart = obj.cart
            # Anonymous users with session cart
            if not request.user.is_authenticated and hasattr(request, 'cart'):
                return cart.id == request.cart.id
            # Authenticated users
            if request.user.is_authenticated:
                return cart.user == request.user if cart.user else False
            return False
        
        # Handle Cart objects directly
        elif hasattr(obj, 'user'):
            # Anonymous users with session cart
            if not request.user.is_authenticated and hasattr(request, 'cart'):
                return obj.id == request.cart.id
            # Authenticated users
            if request.user.is_authenticated:
                return obj.user == request.user if obj.user else False
            return False
        
        return False