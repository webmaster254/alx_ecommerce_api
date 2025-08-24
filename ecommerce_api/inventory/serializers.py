from rest_framework import serializers
from .models import Supplier, Inventory, StockMovement, PurchaseOrder, PurchaseOrderItem, StockAdjustment
from products.models import Product

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    available_stock = serializers.IntegerField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Inventory
        fields = '__all__'
        read_only_fields = ('last_updated',)

class StockMovementSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    product_name = serializers.CharField(source='inventory.product.name', read_only=True)

    class Meta:
        model = StockMovement
        fields = '__all__'
        read_only_fields = ('created_at',)

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'
        read_only_fields = ('purchase_order',)

    def get_total_cost(self, obj):
        return obj.quantity * obj.unit_cost

class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'order_number')

    def get_total_cost(self, obj):
        return sum(item.quantity * item.unit_cost for item in obj.items.all())

class StockAdjustmentSerializer(serializers.ModelSerializer):
    adjusted_by_username = serializers.CharField(source='adjusted_by.username', read_only=True)
    product_name = serializers.CharField(source='inventory.product.name', read_only=True)

    class Meta:
        model = StockAdjustment
        fields = '__all__'
        read_only_fields = ('created_at',)