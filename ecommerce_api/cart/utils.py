from .models import Cart

def get_or_create_cart(request):
    """Utility function to get or create cart for request"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        # Merge session cart with user cart if exists
        if hasattr(request, 'cart') and request.cart and request.cart != cart:
            cart.merge_with_session_cart(request.cart)
            del request.session['cart_id']
        return cart
    elif hasattr(request, 'cart'):
        return request.cart
    else:
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id
        return cart

def transfer_cart_to_user(session_cart, user):
    """Transfer session cart to user after login"""
    user_cart, created = Cart.objects.get_or_create(user=user)
    user_cart.merge_with_session_cart(session_cart)
    return user_cart