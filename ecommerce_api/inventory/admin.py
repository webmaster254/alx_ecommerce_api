from django.contrib import admin
from .models import Supplier, Inventory, StockMovement, PurchaseOrder, PurchaseOrderItem, StockAdjustment

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone', 'created_at')
    search_fields = ('name', 'contact_person', 'email')
    list_filter = ('created_at',)

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'stock_level', 'reserved_stock', 'available_stock', 'is_low_stock_display', 'last_updated')
    list_filter = ('last_updated',)  # Removed is_low_stock from list_filter
    search_fields = ('product__name',)
    readonly_fields = ('available_stock', 'is_low_stock_display', 'last_updated')
    
    def is_low_stock_display(self, obj):
        return obj.is_low_stock()
    is_low_stock_display.short_description = 'Low Stock'
    is_low_stock_display.boolean = True  # Shows nice check/x icons

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('inventory', 'movement_type', 'quantity', 'reference', 'created_by', 'created_at')
    list_filter = ('movement_type', 'created_at')
    search_fields = ('inventory__product__name', 'reference')
    readonly_fields = ('created_at',)

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    readonly_fields = ('total_cost_display',)
    
    def total_cost_display(self, obj):
        return obj.quantity * obj.unit_cost
    total_cost_display.short_description = 'Total Cost'

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'supplier', 'status', 'expected_delivery', 'created_by', 'created_at')
    list_filter = ('status', 'created_at', 'expected_delivery')
    search_fields = ('order_number', 'supplier__name')
    inlines = [PurchaseOrderItemInline]
    readonly_fields = ('order_number', 'created_at', 'updated_at')

@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('inventory', 'adjustment_type', 'quantity', 'reason', 'adjusted_by', 'created_at')
    list_filter = ('adjustment_type', 'created_at')
    search_fields = ('inventory__product__name', 'reason')
    readonly_fields = ('created_at',)