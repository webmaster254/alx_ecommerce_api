from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Cart, CartItem, SavedCart
from products.models import Product

User = get_user_model()

class CartItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'notes', 'total_price', 'is_available']
    
    def get_total_price(self, obj):
        return obj.total_price
    
    def get_is_available(self, obj):
        return obj.is_available

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_key', 'guest_email', 'items', 
                 'subtotal', 'tax_amount', 'total', 'total_items', 'created_at', 'updated_at']

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist")
        return value
    
    def validate(self, data):
        product = Product.objects.get(id=data['product_id'])
        if data['quantity'] > product.quantity:
            raise serializers.ValidationError(
                f"Requested quantity exceeds available stock. Only {product.quantity} available."
            )
        return data

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity', 'notes']
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value

class SavedCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedCart
        fields = ['id', 'user', 'name', 'items', 'created_at', 'updated_at']



class SavedCartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = CartItem  # Or your saved cart item model if different
        fields = ['product', 'quantity']


class SavedCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    items = SavedCartItemSerializer(many=True)

    class Meta:
        model = SavedCart
        fields = ['id', 'user', 'name', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        # user is already set by HiddenField, so no need to manually pass
        saved_cart = SavedCart.objects.create(**validated_data)

        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            if quantity > product.quantity:
                raise serializers.ValidationError("Insufficient stock for product in saved cart.")
            saved_cart.items.create(product=product, quantity=quantity)

        return saved_cart

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']
                if quantity > product.quantity:
                    raise serializers.ValidationError("Insufficient stock for product in saved cart.")
                instance.items.create(product=product, quantity=quantity)

        return instance


class CartItemAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exist")
        return value