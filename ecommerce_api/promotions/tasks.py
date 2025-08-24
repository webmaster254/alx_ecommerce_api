from celery import shared_task
from django.utils import timezone
from .models import Coupon, Promotion, PromoBanner

@shared_task
def deactivate_expired_promotions_task():
    """
    Celery task to deactivate expired promotions
    """
    now = timezone.now()
    Promotion.objects.filter(
        end_date__lt=now,
        is_active=True
    ).update(is_active=False)

@shared_task
def deactivate_expired_coupons_task():
    """
    Celery task to deactivate expired coupons
    """
    now = timezone.now()
    Coupon.objects.filter(
        valid_to__lt=now,
        is_active=True
    ).update(is_active=False)

@shared_task
def deactivate_expired_banners_task():
    """
    Celery task to deactivate expired banners
    """
    now = timezone.now()
    PromoBanner.objects.filter(
        end_date__lt=now,
        is_active=True
    ).update(is_active=False)

@shared_task
def send_promotion_notifications():
    """
    Task to send notifications for upcoming promotions
    """
    # Implementation would depend on your notification system
    pass