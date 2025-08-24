from rest_framework import serializers
from .models import Cart, CartItem, SavedCart
from products.serializers import ProductSerializer
from products.models import Product 

class CartItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_details', 'quantity',
            'total_price', 'is_available', 'added_at', 'updated_at'
        ]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    tax_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'session_key', 'guest_email', 'guest_name',
            'items', 'total_items', 'subtotal', 'tax_amount', 'total',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['session_key']

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        product_id = data['product_id']
        quantity = data['quantity']
    
        try:
            product = Product.objects.get(id=product_id)
            if product.quantity < quantity:   
                raise serializers.ValidationError(
                    f"Only {product.quantity} items available in stock"
                )
            data['product'] = product
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        
        return data


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

        
class SavedCartSerializer(serializers.ModelSerializer):
    items = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=CartItem.objects.all(),
        required=False
    )

    class Meta:
        model = SavedCart
        fields = ['id', 'name', 'items', 'created_at', 'updated_at']