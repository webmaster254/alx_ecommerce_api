# orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem, Payment, Shipping

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'payment_status', 'total', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at', 'updated_at']
    search_fields = ['order_number', 'user__email', 'email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Customer Information', {
            'fields': ('email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_state', 
                      'shipping_zip_code', 'shipping_country')
        }),
        ('Billing Address', {
            'fields': ('billing_address', 'billing_city', 'billing_state',
                      'billing_zip_code', 'billing_country')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax_amount', 'shipping_cost', 'discount_amount', 'total')
        }),
        ('Payment', {
            'fields': ('payment_method', 'transaction_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price', 'total_price']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['product__name', 'order__order_number']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'order', 'payment_method', 'amount', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'order__order_number']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ['order', 'shipping_method', 'status', 'tracking_number', 'shipping_cost']
    list_filter = ['status', 'shipping_method', 'created_at']
    search_fields = ['tracking_number', 'order__order_number']
    readonly_fields = ['created_at', 'updated_at']