from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from products.models import Product

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        null=True,
        blank=True
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    guest_email = models.EmailField(null=True, blank=True)
    guest_name = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.email}"
        elif self.guest_email:
            return f"Guest cart for {self.guest_email}"
        else:
            return f"Anonymous cart ({self.session_key})"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def tax_amount(self):
        # Simplified tax calculation (8%)
        return self.subtotal * Decimal('0.08')

    @property
    def total(self):
        return self.subtotal + self.tax_amount

    def clear(self):
        """Clear all items from cart"""
        self.items.all().delete()

    def merge_with_session_cart(self, session_cart):
        """Merge session cart with user cart after login"""
        if session_cart and session_cart != self:
            for session_item in session_cart.items.all():
                # Check if item already exists in user cart
                existing_item = self.items.filter(product=session_item.product).first()
                if existing_item:
                    existing_item.quantity += session_item.quantity
                    existing_item.save()
                else:
                    session_item.cart = self
                    session_item.save()
            session_cart.delete()

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        null=True, blank=True 
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    notes = models.TextField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        unique_together = ['cart', 'product']
        ordering = ['added_at']

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def save(self, *args, **kwargs):
        # Ensure quantity doesn't exceed available stock
        if self.quantity > self.product.quantity:
            self.quantity = self.product.quantity
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.quantity * self.product.price

    @property
    def is_available(self):
        return self.product.quantity >= self.quantity

class SavedCart(models.Model):
    """For saving carts for later (wishlist functionality)"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_carts'
    )
    name = models.CharField(max_length=100)
    items = models.ManyToManyField(CartItem, related_name='saved_in_carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} - {self.user.email}"