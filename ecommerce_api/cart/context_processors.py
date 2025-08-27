from .models import Cart
from django.db import DatabaseError

def cart_context(request):
    """Make cart available in all templates"""
    cart = None
    cart_item_count = 0

    try:
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item_count = cart.total_items
        elif 'cart_id' in request.session:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'])
                cart_item_count = cart.total_items
            except Cart.DoesNotExist:
                pass
    except DatabaseError:
        # If transaction broken or DB error during template rendering, fail silently
        cart = None
        cart_item_count = 0

    return {
        'cart': cart,
        'cart_item_count': cart_item_count
    }
