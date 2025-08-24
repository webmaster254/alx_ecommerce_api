from .models import Cart

class CartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ensure cart exists for anonymous users
        if not request.user.is_authenticated and 'cart_id' not in request.session:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
            request.cart = cart
        elif not request.user.is_authenticated and 'cart_id' in request.session:
            try:
                request.cart = Cart.objects.get(id=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id
                request.cart = cart
        
        response = self.get_response(request)
        return response