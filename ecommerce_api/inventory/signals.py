from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from orders.models import Order, OrderItem  # Assuming you have an Order model
from .models import Inventory, StockMovement

@receiver(post_save, sender=Order)
def reserve_stock_on_order(sender, instance, created, **kwargs):
    if created and instance.status == 'confirmed':
        for item in instance.items.all():
            try:
                inventory = Inventory.objects.get(product=item.product)
                if inventory.available_stock() >= item.quantity:
                    inventory.reserved_stock += item.quantity
                    inventory.save()
                    
                    # Create stock movement record
                    StockMovement.objects.create(
                        inventory=inventory,
                        movement_type='reserve',
                        quantity=item.quantity,
                        reference=f"Order #{instance.id}",
                        created_by=instance.user
                    )
            except Inventory.DoesNotExist:
                # Handle product without inventory record
                pass

@receiver(post_save, sender=Order)
def release_stock_on_order_cancellation(sender, instance, **kwargs):
    if instance.status == 'cancelled':
        for item in instance.items.all():
            try:
                inventory = Inventory.objects.get(product=item.product)
                inventory.reserved_stock -= item.quantity
                inventory.save()
                
                # Create stock movement record
                StockMovement.objects.create(
                    inventory=inventory,
                    movement_type='release',
                    quantity=item.quantity,
                    reference=f"Order Cancelled #{instance.id}",
                    created_by=instance.user
                )
            except Inventory.DoesNotExist:
                pass

@receiver(post_save, sender=Order)
def reduce_stock_on_order_completion(sender, instance, **kwargs):
    if instance.status == 'completed':
        for item in instance.items.all():
            try:
                inventory = Inventory.objects.get(product=item.product)
                inventory.stock_level -= item.quantity
                inventory.reserved_stock -= item.quantity
                inventory.save()
                
                # Create stock movement record
                StockMovement.objects.create(
                    inventory=inventory,
                    movement_type='out',
                    quantity=item.quantity,
                    reference=f"Order Completed #{instance.id}",
                    created_by=instance.user
                )
            except Inventory.DoesNotExist:
                pass