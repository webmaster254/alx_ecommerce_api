from django.db import transaction
from django.utils import timezone
from .models import Inventory, StockMovement, StockAdjustment
from django.core.exceptions import ValidationError
from .models import Inventory, StockMovement, StockAdjustment, PurchaseOrder

class InventoryUtils:
    """
    Utility class for inventory-related operations
    """
    
    @staticmethod
    def update_stock_level(inventory, quantity, movement_type, reference='', notes='', user=None):
        """
        Update inventory stock level and create stock movement record
        """
        with transaction.atomic():
            # Update inventory based on movement type
            if movement_type == 'in':
                inventory.stock_level += quantity
            elif movement_type == 'out':
                inventory.stock_level = max(0, inventory.stock_level - quantity)
            elif movement_type == 'reserve':
                inventory.reserved_stock += quantity
            elif movement_type == 'release':
                inventory.reserved_stock = max(0, inventory.reserved_stock - quantity)
            else:
                raise ValidationError(f"Invalid movement type: {movement_type}")
            
            inventory.save()
            
            # Create stock movement record
            StockMovement.objects.create(
                inventory=inventory,
                movement_type=movement_type,
                quantity=quantity,
                reference=reference,
                notes=notes,
                created_by=user
            )
    
    @staticmethod
    def adjust_stock(inventory, adjustment_type, quantity, reason, user=None):
        """
        Handle stock adjustments with proper validation
        """
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")
        
        with transaction.atomic():
            # Create stock adjustment record
            adjustment = StockAdjustment.objects.create(
                inventory=inventory,
                adjustment_type=adjustment_type,
                quantity=quantity,
                reason=reason,
                adjusted_by=user
            )
            
            # Update inventory based on adjustment type
            if adjustment_type == 'add':
                inventory.stock_level += quantity
            elif adjustment_type == 'remove':
                inventory.stock_level = max(0, inventory.stock_level - quantity)
            elif adjustment_type == 'correction':
                inventory.stock_level = quantity
            else:
                raise ValidationError(f"Invalid adjustment type: {adjustment_type}")
            
            inventory.save()
            
            # Create stock movement record
            StockMovement.objects.create(
                inventory=inventory,
                movement_type='adjust',
                quantity=quantity,
                reference=f"ADJ-{adjustment.id}",
                notes=f"Stock adjustment: {reason}",
                created_by=user
            )
        
        return adjustment
    
    @staticmethod
    def get_low_stock_items(threshold=None):
        """
        Get all inventory items that are low on stock
        """
        low_stock_items = []
        inventory_items = Inventory.objects.select_related('product').all()
        
        for item in inventory_items:
            available_stock = item.available_stock()
            low_threshold = threshold or item.low_stock_threshold
            
            if available_stock <= low_threshold:
                low_stock_items.append({
                    'inventory': item,
                    'available_stock': available_stock,
                    'threshold': low_threshold
                })
        
        return low_stock_items
    
    @staticmethod
    def generate_order_number():
        """
        Generate a unique purchase order number
        """
        today = timezone.now().strftime('%Y%m%d')
        last_order = PurchaseOrder.objects.filter(
            order_number__startswith=f"PO-{today}"
        ).order_by('order_number').last()
        
        if last_order:
            last_number = int(last_order.order_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"PO-{today}-{new_number:04d}"


class StockValidator:
    """
    Validation utilities for stock operations
    """
    
    @staticmethod
    def validate_stock_availability(inventory, required_quantity):
        """
        Check if sufficient stock is available
        """
        available_stock = inventory.available_stock()
        if available_stock < required_quantity:
            raise ValidationError(
                f"Insufficient stock. Available: {available_stock}, Required: {required_quantity}"
            )
        return True
    
    @staticmethod
    def validate_positive_quantity(quantity):
        """
        Validate that quantity is positive
        """
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero")
        return True


class InventoryReports:
    """
    Utility class for generating inventory reports
    """
    
    @staticmethod
    def get_stock_movement_report(start_date, end_date, product_id=None):
        """
        Generate stock movement report for a given period
        """
        movements = StockMovement.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).select_related('inventory__product', 'created_by')
        
        if product_id:
            movements = movements.filter(inventory__product_id=product_id)
        
        return movements
    
    @staticmethod
    def get_inventory_summary():
        """
        Get summary of inventory status
        """
        total_items = Inventory.objects.count()
        low_stock_items = len(InventoryUtils.get_low_stock_items())
        out_of_stock_items = Inventory.objects.filter(stock_level=0).count()
        
        total_value = sum(
            inventory.product.price * inventory.stock_level 
            for inventory in Inventory.objects.select_related('product').all()
            if hasattr(inventory.product, 'price')
        )
        
        return {
            'total_items': total_items,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'total_value': total_value
        }