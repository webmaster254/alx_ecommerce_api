from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Coupon, Promotion, CouponUsage, PromotionUsage
from decimal import Decimal

class PromotionUtils:
    @staticmethod
    def validate_coupon(coupon_code, user, order_amount=0):
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
        except Coupon.DoesNotExist:
            return {
                'is_valid': False,
                'message': 'Invalid coupon code',
                'discount_amount': Decimal('0.00')
            }
        
        # Check validity period
        now = timezone.now()
        if not (coupon.valid_from <= now <= coupon.valid_to):
            return {
                'is_valid': False,
                'message': 'Coupon is not currently valid',
                'discount_amount': Decimal('0.00')
            }
        
        # Check usage limits
        if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
            return {
                'is_valid': False,
                'message': 'Coupon usage limit reached',
                'discount_amount': Decimal('0.00')
            }
        
        # Check user usage limit
        if user.is_authenticated:
            user_usage_count = CouponUsage.objects.filter(coupon=coupon, user=user).count()
            if user_usage_count >= coupon.user_usage_limit:
                return {
                    'is_valid': False,
                    'message': 'You have reached the usage limit for this coupon',
                    'discount_amount': Decimal('0.00')
                }
        
        # Check minimum order amount
        if coupon.min_order_amount and order_amount < coupon.min_order_amount:
            return {
                'is_valid': False,
                'message': f'Minimum order amount of {coupon.min_order_amount} required',
                'discount_amount': Decimal('0.00')
            }
        
        # Calculate discount
        discount_amount = coupon.calculate_discount(order_amount)
        
        return {
            'is_valid': True,
            'message': 'Coupon applied successfully',
            'discount_amount': discount_amount,
            'coupon': coupon
        }
    
    @staticmethod
    def get_active_promotions():
        now = timezone.now()
        return Promotion.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).prefetch_related('products', 'categories').order_by('-display_priority')
    
    @staticmethod
    def get_product_promotions(product):
        active_promotions = PromotionUtils.get_active_promotions()
        product_promotions = []
        
        for promotion in active_promotions:
            if promotion.applicable_to_all_products:
                product_promotions.append(promotion)
            elif product in promotion.products.all():
                product_promotions.append(promotion)
            elif any(category in promotion.categories.all() for category in product.categories.all()):
                product_promotions.append(promotion)
        
        return product_promotions
    
    @staticmethod
    def record_coupon_usage(coupon, user, order, discount_amount):
        CouponUsage.objects.create(
            coupon=coupon,
            user=user,
            order=order,
            discount_amount=discount_amount
        )
        coupon.usage_count += 1
        coupon.save()
    
    @staticmethod
    def record_promotion_usage(promotion, user, order, discount_amount):
        PromotionUsage.objects.create(
            promotion=promotion,
            user=user,
            order=order,
            discount_amount=discount_amount
        )