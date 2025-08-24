from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, SavedCart
from .serializers import (
    CartSerializer, CartItemSerializer, AddToCartSerializer,
    UpdateCartItemSerializer, SavedCartSerializer
)
from .permissions import IsCartOwner

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
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            return cart
        elif hasattr(self.request, 'cart'):
            return self.request.cart
        return None

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            cart = self.get_object()
            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']
            
            # Check if item already exists in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = self.get_object()
        cart.clear()
        return Response({'status': 'cart cleared'})

    @action(detail=False, methods=['get'])
    def count(self, request):
        cart = self.get_object()
        return Response({'count': cart.total_items})

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCartOwner]
    
    def get_queryset(self):
        cart = self.get_cart()
        if cart:
            return CartItem.objects.filter(cart=cart)
        return CartItem.objects.none()

    def get_cart(self):
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            return cart
        elif hasattr(self.request, 'cart'):
            return self.request.cart
        return None

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
        cart, created = Cart.objects.get_or_create(user=request.user)
        
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