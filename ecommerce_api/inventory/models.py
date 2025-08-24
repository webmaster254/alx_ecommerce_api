from django.db import models
from django.conf import settings
from products.models import Product
from django.core.validators import MinValueValidator

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    stock_level = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    low_stock_threshold = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    reserved_stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    last_updated = models.DateTimeField(auto_now=True)
    
    def available_stock(self):
        return self.stock_level - self.reserved_stock
    
    def is_low_stock(self):
        return self.available_stock() <= self.low_stock_threshold
    
    def __str__(self):
        return f"{self.product.name} - Stock: {self.stock_level}"

class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('reserve', 'Reserve'),
        ('release', 'Release'),
        ('adjust', 'Adjustment'),
    )
    
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    reference = models.CharField(max_length=255, blank=True)  # Order ID, etc.
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PurchaseOrder(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('ordered', 'Ordered'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    )
    
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    expected_delivery = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    received_quantity = models.IntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)

class StockAdjustment(models.Model):
    ADJUSTMENT_TYPES = (
        ('add', 'Add Stock'),
        ('remove', 'Remove Stock'),
        ('correction', 'Stock Correction'),
    )
    
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    adjustment_type = models.CharField(max_length=10, choices=ADJUSTMENT_TYPES)
    quantity = models.IntegerField()
    reason = models.TextField()
    adjusted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)