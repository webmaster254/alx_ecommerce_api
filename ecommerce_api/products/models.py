from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from taggit.managers import TaggableManager  # Added for tagging

CustomUser = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse('products:brand_detail', kwargs={'pk': self.pk})

class Product(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('DISCONTINUED', 'Discontinued'),
        ('ARCHIVED', 'Archived'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sku = models.CharField(max_length=100, unique=True)
    barcode = models.CharField(max_length=100, blank=True)
    quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    # Add tags for products
    tags = TaggableManager(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    is_featured = models.BooleanField(default=False)
    is_digital = models.BooleanField(default=False)
    
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    length = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.TextField(blank=True)
    
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='products_created')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='products_updated')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['is_featured', 'status']),
            models.Index(fields=['name']),  # Added for search optimization
        ]

    def __str__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if self.status == 'ACTIVE' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def reduce_stock(self, quantity):
        """Reduce stock quantity - required by the specifications"""
        if self.quantity >= quantity:
            self.quantity -= quantity
            self.save()
            return True
        return False
    

    @property
    def is_in_stock(self):
        return self.quantity > 0

    @property
    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold

    @property
    def discount_percentage(self):
        if self.compare_price and self.compare_price > self.price:
            return int(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0
        
    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(sum([review.rating for review in reviews]) / reviews.count(), 1)
        return 0
        
    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()
    
    @property
    def primary_image(self):
        """Get the primary image or first available image"""
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary
        return self.images.first()
    
    @property
    def image_url(self):
        """Get URL of primary image"""
        primary = self.primary_image
        if primary and primary.image:
            return primary.image.url
        return None
    
    def get_images(self):
        """Get all images ordered properly"""
        return self.images.all().order_by('is_primary', 'order')

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Image for {self.product.name}"

class ProductReview(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.email} for {self.product.name}"

class ProductActivity(models.Model):
    ACTION_CHOICES = [
        ('view', 'Product View'),
        ('purchase', 'Product Purchase'),
        ('review', 'Product Review'),
        ('wishlist_add', 'Added to Wishlist'),
        ('wishlist_remove', 'Removed from Wishlist'),
        ('price_change', 'Price Change'),
        ('stock_update', 'Stock Update'),
        ('status_change', 'Status Change'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['product', 'action']),
            models.Index(fields=['user', 'action']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.action} - {self.product.name}"

class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"