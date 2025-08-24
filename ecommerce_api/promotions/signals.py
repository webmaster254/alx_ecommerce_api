from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models, transaction
from .models import Coupon, Promotion, PromoBanner, CouponUsage, PromotionUsage

@receiver(pre_save, sender=Coupon)
def validate_coupon_dates(sender, instance, **kwargs):
    """
    Validate that coupon end date is after start date
    """
    if instance.valid_to <= instance.valid_from:
        raise ValidationError("End date must be after start date")

@receiver(pre_save, sender=Promotion)
def validate_promotion_dates(sender, instance, **kwargs):
    """
    Validate that promotion end date is after start date
    """
    if instance.end_date <= instance.start_date:
        raise ValidationError("End date must be after start date")

@receiver(pre_save, sender=PromoBanner)
def validate_banner_dates(sender, instance, **kwargs):
    """
    Validate that banner end date is after start date
    """
    if instance.end_date <= instance.start_date:
        raise ValidationError("End date must be after start date")

@receiver(pre_save, sender=Coupon)
def validate_coupon_discount_values(sender, instance, **kwargs):
    """
    Validate coupon discount values based on type
    """
    if instance.discount_type == 'percentage' and instance.discount_value > 100:
        raise ValidationError("Percentage discount cannot exceed 100%")
    
    if instance.discount_type == 'percentage' and instance.discount_value <= 0:
        raise ValidationError("Percentage discount must be greater than 0")
    
    if instance.discount_type == 'fixed' and instance.discount_value <= 0:
        raise ValidationError("Fixed discount must be greater than 0")

@receiver(pre_save, sender=Promotion)
def validate_promotion_discount_values(sender, instance, **kwargs):
    """
    Validate promotion discount values
    """
    if instance.discount_percentage and (instance.discount_percentage <= 0 or instance.discount_percentage > 100):
        raise ValidationError("Discount percentage must be between 0 and 100")
    
    if instance.discount_amount and instance.discount_amount <= 0:
        raise ValidationError("Discount amount must be greater than 0")
    
    # Ensure at least one discount type is specified if not free shipping
    if not instance.is_free_shipping and not instance.discount_percentage and not instance.discount_amount:
        raise ValidationError("Either discount percentage, discount amount, or free shipping must be specified")

@receiver(post_save, sender=CouponUsage)
def update_coupon_usage_count(sender, instance, created, **kwargs):
    """
    Update coupon usage count when a new usage is recorded
    """
    if created:
        with transaction.atomic():
            coupon = instance.coupon
            coupon.usage_count = CouponUsage.objects.filter(coupon=coupon).count()
            coupon.save()

@receiver(pre_save, sender=Coupon)
def generate_coupon_code_if_empty(sender, instance, **kwargs):
    """
    Automatically generate a coupon code if not provided
    """
    if not instance.code:
        from django.utils.crypto import get_random_string
        import string
        
        # Generate a random coupon code (8 characters, uppercase and digits)
        chars = string.ascii_uppercase + string.digits
        random_code = get_random_string(8, chars)
        
        # Check if code already exists
        while Coupon.objects.filter(code=random_code).exists():
            random_code = get_random_string(8, chars)
        
        instance.code = random_code

@receiver(pre_save, sender=PromoBanner)
def validate_banner_display_order(sender, instance, **kwargs):
    """
    Ensure display order is unique for active banners
    """
    if instance.display_order is not None:
        # Check if another active banner has the same display order
        conflicting_banners = PromoBanner.objects.filter(
            display_order=instance.display_order,
            is_active=True
        ).exclude(pk=instance.pk)
        
        if conflicting_banners.exists():
            # Find the next available display order
            max_order = PromoBanner.objects.filter(is_active=True).aggregate(
                models.Max('display_order')
            )['display_order__max'] or 0
            instance.display_order = max_order + 1

@receiver(pre_save, sender=Coupon)
def deactivate_expired_coupon(sender, instance, **kwargs):
    """
    Automatically deactivate coupons that have expired
    """
    now = timezone.now()
    if instance.valid_to < now:
        instance.is_active = False

@receiver(pre_save, sender=Promotion)
def deactivate_expired_promotion(sender, instance, **kwargs):
    """
    Automatically deactivate promotions that have expired
    """
    now = timezone.now()
    if instance.end_date < now:
        instance.is_active = False

@receiver(pre_save, sender=PromoBanner)
def deactivate_expired_banner(sender, instance, **kwargs):
    """
    Automatically deactivate banners that have expired
    """
    now = timezone.now()
    if instance.end_date < now:
        instance.is_active = False

@receiver(post_save, sender=Promotion)
def create_bundle_offer_if_needed(sender, instance, created, **kwargs):
    """
    Automatically create bundle offer if promotion type is bundle
    """
    if created and instance.specific_type == 'bundle':
        from .models import BundleOffer
        # Create a default bundle offer
        BundleOffer.objects.create(
            promotion=instance,
            buy_quantity=2,
            get_quantity=1,
            get_discount_percentage=100  # 100% discount on the free item
        )

@receiver(pre_delete, sender=Coupon)
def prevent_delete_used_coupon(sender, instance, **kwargs):
    """
    Prevent deletion of coupons that have been used
    """
    if instance.usage_count > 0:
        raise ValidationError("Cannot delete coupon that has been used. Deactivate it instead.")

@receiver(pre_delete, sender=Promotion)
def prevent_delete_used_promotion(sender, instance, **kwargs):
    """
    Prevent deletion of promotions that have been used
    """
    if instance.usages.exists():
        raise ValidationError("Cannot delete promotion that has been used. Deactivate it instead.")