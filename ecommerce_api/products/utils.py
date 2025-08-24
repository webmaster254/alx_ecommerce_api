# products/utils.py
import os
import uuid
from django.utils.text import slugify
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
from django.conf import settings
from .models import ProductActivity

def generate_unique_slug(model, value, slug_field='slug'):
    """
    Generate a unique slug for a model instance.
    If the slug already exists, append a number to make it unique.
    """
    slug = slugify(value)
    unique_slug = slug
    num = 1
    while model.objects.filter(**{slug_field: unique_slug}).exists():
        unique_slug = f'{slug}-{num}'
        num += 1
    return unique_slug

def optimize_image(image, max_size=(800, 800), quality=85):
    """
    Optimize an image by resizing and compressing it.
    Returns optimized image content.
    """
    img = Image.open(image)
    
    # Convert to RGB if necessary
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    # Resize if necessary
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Save optimized image
    output = BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)
    
    return ContentFile(output.read(), name=image.name)

def handle_uploaded_image(image_file, upload_to='products/'):
    """
    Handle uploaded image - optimize and save it.
    Returns the file path of the saved image.
    """
    # Generate unique filename
    ext = os.path.splitext(image_file.name)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_to, filename)
    
    # Optimize image
    optimized_image = optimize_image(image_file)
    
    # Save optimized image
    saved_path = default_storage.save(filepath, optimized_image)
    return saved_path

def track_product_activity(product, user, action, **details):
    """
    Track user activity related to products.
    """
    request = details.pop('request', None)
    
    activity_data = {
        'product': product,
        'user': user,
        'action': action,
        'details': details or {}
    }
    
    if request:
        activity_data['ip_address'] = get_client_ip(request)
        activity_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
    
    return ProductActivity.objects.create(**activity_data)

def get_client_ip(request):
    """
    Get the client's IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def calculate_average_rating(product):
    """
    Calculate the average rating for a product.
    """
    reviews = product.reviews.filter(is_approved=True)
    if reviews.exists():
        return round(sum([review.rating for review in reviews]) / reviews.count(), 1)
    return 0

def get_product_recommendations(product, limit=4):
    """
    Get recommended products based on similar category, tags, or other criteria.
    """
    from .models import Product
    
    recommendations = Product.objects.filter(
        status='ACTIVE'
    ).exclude(
        id=product.id
    )
    
    # Prioritize same category
    if product.category:
        same_category = recommendations.filter(category=product.category)
        if same_category.exists():
            return same_category.order_by('?')[:limit]
    
    # Then same tags
    if product.tags.exists():
        same_tags = recommendations.filter(tags__in=product.tags.all()).distinct()
        if same_tags.exists():
            return same_tags.order_by('?')[:limit]
    
    # Fallback to featured products
    return recommendations.filter(is_featured=True).order_by('?')[:limit]

def generate_product_report(products_queryset, format='dict'):
    """
    Generate a report of products with various statistics.
    """
    report = {
        'total_products': products_queryset.count(),
        'active_products': products_queryset.filter(status='ACTIVE').count(),
        'out_of_stock': products_queryset.filter(quantity=0).count(),
        'low_stock': products_queryset.filter(quantity__lte=5, quantity__gt=0).count(),
        'total_value': sum([p.price * p.quantity for p in products_queryset]),
        'average_price': 0,
        'by_category': {},
        'by_status': {}
    }
    
    # Calculate average price
    if report['total_products'] > 0:
        report['average_price'] = report['total_value'] / sum([p.quantity for p in products_queryset])
    
    # Count by category
    for product in products_queryset:
        category_name = product.category.name if product.category else 'Uncategorized'
        report['by_category'][category_name] = report['by_category'].get(category_name, 0) + 1
        
        report['by_status'][product.status] = report['by_status'].get(product.status, 0) + 1
    
    return report

def send_low_stock_notification(product):
    """
    Send notification for low stock products.
    This can be extended to send emails, Slack messages, etc.
    """
    # Placeholder for actual notification logic
    print(f"Low stock alert: {product.name} has only {product.quantity} units left.")
    
    # Example: Send email to admin
    # from django.core.mail import send_mail
    # send_mail(
    #     f'Low Stock Alert: {product.name}',
    #     f'The product {product.name} has only {product.quantity} units left.',
    #     'noreply@yourstore.com',
    #     ['admin@yourstore.com'],
    #     fail_silently=False,
    # )

class ProductInventoryManager:
    """
    Utility class for managing product inventory.
    """
    
    @staticmethod
    def update_stock(product, quantity_change, reason='manual adjustment'):
        """
        Update product stock and track the change.
        """
        old_quantity = product.quantity
        product.quantity += quantity_change
        
        if product.quantity < 0:
            raise ValueError("Cannot set negative stock quantity.")
        
        product.save()
        
        # Track this activity
        track_product_activity(
            product=product,
            user=None,  # Could be system or admin user
            action='stock_update',
            old_quantity=old_quantity,
            new_quantity=product.quantity,
            change=quantity_change,
            reason=reason
        )
        
        # Check if stock is low after update
        if product.is_low_stock:
            send_low_stock_notification(product)
        
        return product
    
    @staticmethod
    def bulk_update_stock(products_quantities, reason='bulk adjustment'):
        """
        Update stock for multiple products at once.
        """
        updated_products = []
        for product, quantity_change in products_quantities:
            updated_products.append(
                ProductInventoryManager.update_stock(product, quantity_change, reason)
            )
        return updated_products