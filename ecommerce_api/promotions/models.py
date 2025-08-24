from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from products.models import Product, Category
from decimal import Decimal

class PromotionType(models.Model):
    """Different types of promotions available"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Coupon(models.Model):
    """Coupon codes for discounts"""
    CODE_TYPES = (
        ('percentage', 'Percentage Discount'),
        ('fixed', 'Fixed Amount Discount'),
        ('free_shipping', 'Free Shipping'),
    )
    
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=CODE_TYPES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Usage limits
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum number of times this coupon can be used")
    usage_count = models.PositiveIntegerField(default=0)
    user_usage_limit = models.PositiveIntegerField(default=1, help_text="Maximum usage per user")
    
    # Validity period
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Applicability
    applicable_to_all_products = models.BooleanField(default=True)
    applicable_categories = models.ManyToManyField(Category, blank=True)
    applicable_products = models.ManyToManyField(Product, blank=True)
    excluded_products = models.ManyToManyField(Product, blank=True, related_name='excluded_coupons')
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()}"
    
    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_to and
            (self.usage_limit is None or self.usage_count < self.usage_limit)
        )
    
    def can_user_use(self, user, usage_count):
        return usage_count < self.user_usage_limit
    
    def calculate_discount(self, order_amount):
        if not self.is_valid():
            return Decimal('0.00')
        
        if self.min_order_amount and order_amount < self.min_order_amount:
            return Decimal('0.00')
        
        if self.discount_type == 'percentage':
            discount = (order_amount * self.discount_value) / 100
            if self.max_discount:
                discount = min(discount, self.max_discount)
        elif self.discount_type == 'fixed':
            discount = min(self.discount_value, order_amount)
        else:  # free_shipping
            discount = Decimal('0.00')  # Shipping cost would be handled separately
        
        return discount

class Promotion(models.Model):
    """General promotions and sales"""
    PROMOTION_TYPES = (
        ('flash_sale', 'Flash Sale'),
        ('seasonal', 'Seasonal Sale'),
        ('clearance', 'Clearance Sale'),
        ('bundle', 'Bundle Offer'),
        ('bogo', 'Buy One Get One'),
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    promotion_type = models.ForeignKey(PromotionType, on_delete=models.CASCADE)
    specific_type = models.CharField(max_length=20, choices=PROMOTION_TYPES, default='flash_sale')
    
    # Discount details
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    is_free_shipping = models.BooleanField(default=False)
    
    # Validity period
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Applicability
    applicable_to_all_products = models.BooleanField(default=False)
    categories = models.ManyToManyField(Category, blank=True)
    products = models.ManyToManyField(Product, blank=True)
    excluded_products = models.ManyToManyField(Product, blank=True, related_name='excluded_promotions')
    
    # Display settings
    banner_image = models.ImageField(upload_to='promotion_banners/', null=True, blank=True)
    display_priority = models.PositiveIntegerField(default=0, help_text="Higher number means higher priority")
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def is_currently_active(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date
    
    def get_discount_amount(self, product_price):
        if self.discount_percentage:
            return (product_price * self.discount_percentage) / 100
        elif self.discount_amount:
            return min(self.discount_amount, product_price)
        return Decimal('0.00')

class BundleOffer(models.Model):
    """Buy X get Y free or at discount"""
    promotion = models.OneToOneField(Promotion, on_delete=models.CASCADE, related_name='bundle_offer')
    buy_quantity = models.PositiveIntegerField(default=1)
    get_quantity = models.PositiveIntegerField(default=1)
    get_discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    get_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    
    def __str__(self):
        return f"Buy {self.buy_quantity} Get {self.get_quantity} - {self.promotion.name}"

class PromotionUsage(models.Model):
    """Track usage of promotions"""
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)  # Assuming you have an Order model
    used_at = models.DateTimeField(auto_now_add=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = [['promotion', 'order']]  # Prevent duplicate usage per order

class CouponUsage(models.Model):
    """Track usage of coupons"""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    used_at = models.DateTimeField(auto_now_add=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = [['coupon', 'order']]  # Prevent duplicate usage per order

class PromoBanner(models.Model):
    """Promotional banners for display"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='promo_banners/')
    link_url = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def is_currently_active(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date
    
    class Meta:
        ordering = ['display_order', '-created_at']