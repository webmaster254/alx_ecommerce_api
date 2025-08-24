# orders/signals.py
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Order, OrderItem

@receiver(post_save, sender=Order)
def update_order_totals(sender, instance, created, **kwargs):
    """Update order totals when order is saved"""
    if created:
        instance.calculate_totals()
        instance.save()

@receiver(post_save, sender=OrderItem)
@receiver(pre_delete, sender=OrderItem)
def update_order_on_item_change(sender, instance, **kwargs):
    """Update order totals when items are added, updated, or deleted"""
    if instance.order:
        instance.order.calculate_totals()
        instance.order.save()