from rest_framework import serializers
from .models import (
    PromotionType, Coupon, Promotion, BundleOffer, 
    PromotionUsage, CouponUsage, PromoBanner
)
from products.serializers import ProductSerializer, CategorySerializer

class PromotionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionType
        fields = '__all__'

class CouponSerializer(serializers.ModelSerializer):
    is_valid = serializers.BooleanField(read_only=True)
    applicable_categories_details = CategorySerializer(source='applicable_categories', many=True, read_only=True)
    applicable_products_details = ProductSerializer(source='applicable_products', many=True, read_only=True)
    usage_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ('usage_count', 'created_at', 'updated_at')

    def get_usage_percentage(self, obj):
        if obj.usage_limit:
            return (obj.usage_count / obj.usage_limit) * 100
        return 0

class PromotionSerializer(serializers.ModelSerializer):
    is_currently_active = serializers.BooleanField(read_only=True)
    categories_details = CategorySerializer(source='categories', many=True, read_only=True)
    products_details = ProductSerializer(source='products', many=True, read_only=True)
    time_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_time_remaining(self, obj):
        from django.utils import timezone
        now = timezone.now()
        if obj.end_date > now:
            return obj.end_date - now
        return None

class BundleOfferSerializer(serializers.ModelSerializer):
    promotion_details = PromotionSerializer(source='promotion', read_only=True)

    class Meta:
        model = BundleOffer
        fields = '__all__'

class PromotionUsageSerializer(serializers.ModelSerializer):
    promotion_name = serializers.CharField(source='promotion.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = PromotionUsage
        fields = '__all__'

class CouponUsageSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = CouponUsage
        fields = '__all__'

class PromoBannerSerializer(serializers.ModelSerializer):
    is_currently_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = PromoBanner
        fields = '__all__'

class ApplyCouponSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(max_length=50)
    order_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

class CouponValidationResponseSerializer(serializers.Serializer):
    is_valid = serializers.BooleanField()
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    message = serializers.CharField()
    coupon = CouponSerializer(read_only=True)

class ActivePromotionsSerializer(serializers.Serializer):
    promotions = PromotionSerializer(many=True)
    banners = PromoBannerSerializer(many=True)