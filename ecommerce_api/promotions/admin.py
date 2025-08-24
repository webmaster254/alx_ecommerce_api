from django.contrib import admin
from .models import (
    PromotionType, Coupon, Promotion, BundleOffer,
    PromotionUsage, CouponUsage, PromoBanner
)

@admin.register(PromotionType)
class PromotionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'usage_count', 'is_active', 'valid_from', 'valid_to')
    list_filter = ('discount_type', 'is_active', 'valid_from', 'valid_to')
    search_fields = ('code', 'description')
    filter_horizontal = ('applicable_categories', 'applicable_products', 'excluded_products')
    readonly_fields = ('usage_count', 'created_at', 'updated_at')

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'promotion_type', 'specific_type', 'is_active', 'start_date', 'end_date')
    list_filter = ('promotion_type', 'specific_type', 'is_active', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    filter_horizontal = ('categories', 'products', 'excluded_products')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(BundleOffer)
class BundleOfferAdmin(admin.ModelAdmin):
    list_display = ('promotion', 'buy_quantity', 'get_quantity')
    list_filter = ('buy_quantity', 'get_quantity')

@admin.register(PromotionUsage)
class PromotionUsageAdmin(admin.ModelAdmin):
    list_display = ('promotion', 'user', 'discount_amount', 'used_at')
    list_filter = ('used_at', 'promotion')
    readonly_fields = ('used_at',)

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'user', 'discount_amount', 'used_at')
    list_filter = ('used_at', 'coupon')
    readonly_fields = ('used_at',)

@admin.register(PromoBanner)
class PromoBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'display_order', 'start_date', 'end_date')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')