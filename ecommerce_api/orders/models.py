# orders/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from products.models import Product
from decimal import Decimal
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='PENDING'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING'
    )
    
    # Shipping information
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_zip_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100)
    
    # Billing information
    billing_address = models.TextField(blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_zip_code = models.CharField(max_length=20, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)
    
    # Contact information
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment information
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Notes
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon = models.ForeignKey('promotions.Coupon', on_delete=models.SET_NULL, null=True, blank=True)


    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['payment_status', 'created_at']),
        ]

    def __str__(self):
        return f"Order #{self.order_number} - {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number: YYMMDDHHMMSS + random 4 digits
            timestamp = timezone.now().strftime('%y%m%d%H%M%S')
            import random
            random_digits = str(random.randint(1000, 9999))
            self.order_number = f"{timestamp}{random_digits}"
        
        # Set billing address to shipping address if not provided
        if not self.billing_address:
            self.billing_address = self.shipping_address
            self.billing_city = self.shipping_city
            self.billing_state = self.shipping_state
            self.billing_zip_code = self.shipping_zip_code
            self.billing_country = self.shipping_country
            
        super().save(*args, **kwargs)

    def update_stock(self):
        """Update product stock quantities when order status changes"""
        if self.status in ['SHIPPED', 'DELIVERED']:
            for item in self.items.all():
                item.product.reduce_stock(item.quantity)

        
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number
            timestamp = timezone.now().strftime('%y%m%d%H%M%S')
            import random
            random_digits = str(random.randint(1000, 9999))
            self.order_number = f"{timestamp}{random_digits}"
        
        # Set billing address to shipping address if not provided
        if not self.billing_address:
            self.billing_address = self.shipping_address
            self.billing_city = self.shipping_city
            self.billing_state = self.shipping_state
            self.billing_zip_code = self.shipping_zip_code
            self.billing_country = self.shipping_country
            
        # If order status is changing to shipped/delivered, update stock
        if self.pk:  # Only for existing orders
            try:
                old_order = Order.objects.get(pk=self.pk)
                if (old_order.status in ['PENDING', 'PROCESSING'] and 
                    self.status in ['SHIPPED', 'DELIVERED']):
                    self.update_stock()
            except Order.DoesNotExist:
                pass
                
        super().save(*args, **kwargs)

    def update_stock(self):
        """Update product stock quantities when order status changes to shipped/delivered"""
        for item in self.items.all():
            try:
                # Use the reduce_stock method from Product model
                item.product.reduce_stock(item.quantity)
                
                # Also create an activity log for the stock change
                from products.models import ProductActivity
                ProductActivity.objects.create(
                    product=item.product,
                    user=None,  # System action
                    action='stock_update',
                    details={
                        'order_number': self.order_number,
                        'quantity_change': -item.quantity,
                        'previous_stock': item.product.quantity + item.quantity,
                        'new_stock': item.product.quantity
                    }
                )
            except Exception as e:
                # Log error but don't break the process
                print(f"Error updating stock for product {item.product.id}: {e}")

    def calculate_totals(self):
        """Calculate order totals based on items"""
        subtotal = sum(item.total_price for item in self.items.all())
        
        # Calculate tax (simplified - you might want a more complex tax calculation)
        self.tax_amount = subtotal * Decimal('0.08')  # 8% tax
        
        # Calculate shipping (simplified)
        self.shipping_cost = Decimal('10.00')  # Flat rate shipping
        
        # Apply discounts if any
        self.total = subtotal + self.tax_amount + self.shipping_cost - self.discount_amount
        self.subtotal = subtotal


    @property
    def item_count(self):
        return self.items.count()

    @property
    def can_be_cancelled(self):
        return self.status in ['PENDING', 'PROCESSING']

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Store product details at time of purchase
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.quantity} x {self.product_name} (Order #{self.order.order_number})"

    def save(self, *args, **kwargs):
        # Store product details at time of purchase
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_sku:
            self.product_sku = self.product.sku
        if not self.price:
            self.price = self.product.price
            
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Store product details at time of purchase
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_sku:
            self.product_sku = self.product.sku
        if not self.price:
            self.price = self.product.price
            
        super().save(*args, **kwargs)
        
        # Recalculate order totals when items change
        if self.order:
            self.order.calculate_totals()
            self.order.save()

    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)
        
        # Recalculate order totals when items are removed
        if order:
            order.calculate_totals()
            order.save()

    @property
    def total_price(self):
        return self.quantity * self.price
    
    

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('PAYPAL', 'PayPal'),
        ('STRIPE', 'Stripe'),
        ('BANK_TRANSFER', 'Bank Transfer'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING'
    )
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_details = models.JSONField(default=dict)  # Store payment gateway response
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment #{self.transaction_id} - {self.amount}"

class Shipping(models.Model):
    SHIPPING_METHOD_CHOICES = [
        ('STANDARD', 'Standard Shipping'),
        ('EXPRESS', 'Express Shipping'),
        ('OVERNIGHT', 'Overnight Shipping'),
        ('PICKUP', 'Store Pickup'),
    ]

    SHIPPING_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='shipping_info'
    )
    shipping_method = models.CharField(
        max_length=20,
        choices=SHIPPING_METHOD_CHOICES,
        default='STANDARD'
    )
    tracking_number = models.CharField(max_length=100, blank=True)
    carrier = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20,
        choices=SHIPPING_STATUS_CHOICES,
        default='PENDING'
    )
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Shipping for Order #{self.order.order_number}"
    
def calculate_totals(self):
    """Calculate order totals based on items"""
    subtotal = sum(item.total_price for item in self.items.all())
    
    # Calculate tax (simplified - you might want a more complex tax calculation)
    self.tax_amount = subtotal * Decimal('0.08')  # 8% tax
    
    # Calculate shipping (simplified)
    self.shipping_cost = Decimal('10.00')  # Flat rate shipping
    
    # Apply discounts if any
    self.total = subtotal + self.tax_amount + self.shipping_cost - self.discount_amount
    self.subtotal = subtotal

def reduce_stock(self, quantity):
    """Reduce product stock - add this to your Product model"""
    if self.quantity >= quantity:
        self.quantity -= quantity
        self.save()
        return True
    return False