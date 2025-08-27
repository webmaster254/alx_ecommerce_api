from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, SavedCart
from .serializers import (
    CartSerializer, CartItemSerializer, AddToCartSerializer,
    UpdateCartItemSerializer, SavedCartSerializer, CartItemAddSerializer
)
from .permissions import IsCartOwner
from products.models import Product


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCartOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Cart.objects.filter(user=user)
        elif hasattr(self.request, 'cart'):
            return Cart.objects.filter(id=self.request.cart.id)
        return Cart.objects.none()

    def get_object(self):
        # Retrieve cart filtered by current user to enforce ownership restrictions
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs.get(self.lookup_field or 'pk'))
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        serializer = CartItemAddSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response(
                    {"error": "Product not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if quantity <= 0:
                return Response(
                    {"error": "Quantity must be positive"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get or create user's cart
            if request.user.is_authenticated:
                cart, _ = Cart.objects.get_or_create(user=request.user)
            elif hasattr(request, 'cart'):
                cart = request.cart
            else:
                return Response(
                    {"error": "Authentication required to add items"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Check if CartItem exists, update or create
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                new_quantity = cart_item.quantity + quantity
                if new_quantity > product.quantity:
                    return Response(
                        {"error": "Insufficient stock"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                cart_item.quantity = new_quantity
                cart_item.save()
            else:
                if quantity > product.quantity:
                    # Rollback creation if quantity invalid
                    cart_item.delete()
                    return Response(
                        {"error": "Insufficient stock"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(
                CartItemSerializer(cart_item).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCartOwner]

    def get_cart(self):
        if self.request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=self.request.user)
            return cart
        elif hasattr(self.request, 'cart'):
            return self.request.cart
        return None

    def get_queryset(self):
        cart = self.get_cart()
        if cart:
            return CartItem.objects.filter(cart=cart)
        return CartItem.objects.none()

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UpdateCartItemSerializer
        return CartItemSerializer

    def perform_create(self, serializer):
        cart = self.get_cart()
        serializer.save(cart=cart)


class SavedCartViewSet(viewsets.ModelViewSet):
    serializer_class = SavedCartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedCart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        saved_cart = self.get_object()
        cart, _ = Cart.objects.get_or_create(user=request.user)

        for saved_item in saved_cart.items.all():
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=saved_item.product,
                defaults={'quantity': saved_item.quantity}
            )
            if not created:
                cart_item.quantity = saved_item.quantity
                cart_item.save()

        return Response(CartSerializer(cart).data)
