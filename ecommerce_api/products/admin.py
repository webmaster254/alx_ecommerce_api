# products/admin.py
from django.contrib import admin
from .models import Product, Category, Brand, ProductImage, ProductReview, ProductActivity, Wishlist
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.urls import path


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    list_editable = ['is_primary', 'order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Product Count'

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'product_count']
    search_fields = ['name']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Product Count'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'


class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    readonly_fields = ['user', 'rating', 'title', 'comment', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'name', 'category', 'price', 'quantity', 'status', 'created_at']
    list_filter = ['status', 'category', 'brand', 'is_featured', 'created_at']
    search_fields = ['name', 'description', 'sku']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    readonly_fields = ['image_preview', 'created_by', 'updated_by', 'created_at', 'updated_at', 'published_at']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('gallery/', self.admin_site.admin_view(self.product_gallery), name='product_gallery'),
        ]
        return custom_urls + urls
    
    def product_gallery(self, request):
        # You can add any context data you need
        context = {
            **self.admin_site.each_context(request),
            'title': 'Product Gallery',
            'products': Product.objects.all().select_related('brand', 'category').prefetch_related('images'),
        }
        return TemplateResponse(request, 'admin/products/product_gallery.html', context)
    
    
    def image_preview(self, obj):
        # Get the primary image or first available image
        primary_image = obj.images.filter(is_primary=True).first()
        if not primary_image:
            primary_image = obj.images.first()
        
        if primary_image and primary_image.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 4px;" />', primary_image.image.url)
        return "No Image"
    image_preview.short_description = 'Image'
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_gallery_link'] = True
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user__email', 'title']
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Selected reviews have been approved.")
    approve_reviews.short_description = "Approve selected reviews"
    
    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, "Selected reviews have been disapproved.")
    disapprove_reviews.short_description = "Disapprove selected reviews"

@admin.register(ProductActivity)
class ProductActivityAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'action', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['product__name', 'user__email']
    readonly_fields = ['product', 'user', 'action', 'ip_address', 'user_agent', 'details', 'timestamp']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__email', 'product__name']