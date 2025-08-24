from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, Payment, Shipping
from .serializers import (
    OrderSerializer, OrderCreateSerializer, 
    OrderItemSerializer, PaymentSerializer, ShippingSerializer
)
from .permissions import IsOrderOwner, IsStaffOrOrderOwner

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrOrderOwner]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.can_be_cancelled:
            order.status = 'CANCELLED'
            order.save()
            return Response({'status': 'order cancelled'})
        return Response(
            {'error': 'Order cannot be cancelled'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        order = self.get_object()
        items = order.items.all()
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrOrderOwner]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(order__user=user)

class ShippingViewSet(viewsets.ModelViewSet):
    queryset = Shipping.objects.all()
    serializer_class = ShippingSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrOrderOwner]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Shipping.objects.all()
        return Shipping.objects.filter(order__user=user)