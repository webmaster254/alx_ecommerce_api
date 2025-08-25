# products/serializers.py
from rest_framework import serializers
from .models import Product, Category, Brand, ProductReview, Wishlist, ProductImage
from django.contrib.auth import get_user_model
from taggit.serializers import TaggitSerializer, TagListSerializerField

CustomUser = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'product_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

class BrandSerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'website', 'product_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProductImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

class ProductReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = ProductReview
        fields = [
            'id', 'product', 'product_name', 'user', 'user_email', 'user_name',
            'rating', 'title', 'comment', 'is_approved', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def create(self, validated_data):
        # Ensure a user can only review a product once
        user = self.context['request'].user
        product = validated_data['product']
        
        if ProductReview.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("You have already reviewed this product.")
        
        validated_data['user'] = user
        return super().create(validated_data)

class ProductSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    updated_by_email = serializers.CharField(source='updated_by.email', read_only=True)
    
    # Computed fields
    is_in_stock = serializers.BooleanField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'compare_price', 'cost',
            'sku', 'barcode', 'quantity', 'low_stock_threshold', 'category', 'category_name',
            'brand', 'brand_name', 'tags', 'status', 'is_featured', 'is_digital',
            'weight', 'length', 'width', 'height', 'seo_title', 'seo_description',
            'created_by', 'created_by_email', 'updated_by', 'updated_by_email',
            'created_at', 'updated_at', 'published_at', 'images',
            'is_in_stock', 'is_low_stock', 'discount_percentage',
            'average_rating', 'review_count'
        ]
        read_only_fields = [
            'id', 'slug', 'created_by', 'updated_by', 'created_at', 'updated_at',
            'published_at', 'is_in_stock', 'is_low_stock', 'discount_percentage',
            'average_rating', 'review_count'
        ]
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value
    
    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value
    
    def validate(self, data):
        # Ensure compare_price is greater than price if provided
        compare_price = data.get('compare_price')
        price = data.get('price')
        
        if compare_price and price and compare_price <= price:
            raise serializers.ValidationError({
                'compare_price': 'Compare price must be greater than regular price.'
            })
        
        return data
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['updated_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super().update(instance, validated_data)

class WishlistSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    product_image = serializers.SerializerMethodField()
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'product_name', 'product_price', 'product_image', 'product_slug', 'added_at']
        read_only_fields = ['id', 'user', 'added_at']
    
    def get_product_image(self, obj):
        primary_image = obj.product.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image.image.url
        first_image = obj.product.images.first()
        if first_image:
            return first_image.image.url
        return None
    
    def create(self, validated_data):
        user = self.context['request'].user
        product = validated_data['product']
        
        # Check if product is already in wishlist
        if Wishlist.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("Product is already in your wishlist.")
        
        validated_data['user'] = user
        return super().create(validated_data)

class ProductSearchSerializer(serializers.Serializer):
    q = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)
    brand = serializers.CharField(required=False, allow_blank=True)
    min_price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    max_price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    ordering = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    
    def validate_min_price(self, value):
        if value and value < 0:
            raise serializers.ValidationError("Minimum price cannot be negative.")
        return value
    
    def validate_max_price(self, value):
        if value and value < 0:
            raise serializers.ValidationError("Maximum price cannot be negative.")
        return value