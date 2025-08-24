from django.contrib import admin
from .models import Cart, CartItem, SavedCart

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'guest_email', 'total_items', 'subtotal', 'total', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'guest_email', 'session_key']
    readonly_fields = ['session_key', 'created_at', 'updated_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity', 'total_price', 'is_available']
    list_filter = ['added_at', 'updated_at']
    search_fields = ['product__name', 'cart__user__email']
    readonly_fields = ['added_at', 'updated_at']

@admin.register(SavedCart)
class SavedCartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'name']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['items']  