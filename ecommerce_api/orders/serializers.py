# orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem, Payment, Shipping
from products.serializers import ProductSerializer
from decimal import Decimal


class OrderItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_details', 'quantity', 'price',
            'product_name', 'product_sku', 'total_price', 'created_at'
        ]
        read_only_fields = ['product_name', 'product_sku', 'price']

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'user_email', 'status', 'payment_status',
            'shipping_address', 'shipping_city', 'shipping_state', 'shipping_zip_code',
            'shipping_country', 'billing_address', 'billing_city', 'billing_state',
            'billing_zip_code', 'billing_country', 'email', 'phone', 'subtotal',
            'tax_amount', 'shipping_cost', 'discount_amount', 'total', 'payment_method',
            'transaction_id', 'items', 'item_count', 'customer_notes', 'admin_notes',
            'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at'
        ]
        read_only_fields = [
            'order_number', 'subtotal', 'tax_amount', 'shipping_cost',
            'discount_amount', 'total', 'created_at', 'updated_at'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'shipping_address', 'shipping_city', 'shipping_state',
            'shipping_zip_code', 'shipping_country', 'billing_address',
            'billing_city', 'billing_state', 'billing_zip_code',
            'billing_country', 'email', 'phone', 'customer_notes', 'items'
        ]

    from decimal import Decimal

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        # Provide default zeros for required calculated fields
        order = Order.objects.create(
            subtotal=Decimal('0.00'),
            tax_amount=Decimal('0.00'),
            shipping_cost=Decimal('0.00'),
            discount_amount=Decimal('0.00'),
            total=Decimal('0.00'),
            **validated_data
        )
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        order.calculate_totals()  # implement this method to sum items and update order
        order.save()

        return order

    

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'payment_method', 'amount', 'status',
            'transaction_id', 'payment_details', 'created_at',
            'updated_at', 'completed_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = [
            'id', 'order', 'shipping_method', 'tracking_number',
            'carrier', 'status', 'estimated_delivery', 'actual_delivery',
            'shipping_cost', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']