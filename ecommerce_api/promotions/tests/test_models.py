from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from promotions.models import (
    PromotionType, Coupon, Promotion, BundleOffer,
    PromotionUsage, CouponUsage, PromoBanner
)
from products.models import Category, Product
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from orders.models import Order  # Import your actual Order model

User = get_user_model()

class PromotionModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='pass')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product', slug='test-product', price=Decimal('50.00'),
            sku='TP001', quantity=10, status='ACTIVE'
        )
        self.promo_type = PromotionType.objects.create(name='Seasonal', description='Seasonal sales promotion')
    
    def test_promotion_type_str(self):
        self.assertEqual(str(self.promo_type), 'Seasonal')

    def test_coupon_validity_and_discount(self):
        coupon = Coupon.objects.create(
            code='DISCOUNT10',
            discount_type='percentage',
            discount_value=Decimal('10.00'),
            valid_from=timezone.now(),
            valid_to=timezone.now() + timezone.timedelta(days=10),
            is_active=True,
            created_by=self.user
        )
        self.assertTrue(coupon.is_valid())
        discount = coupon.calculate_discount(Decimal('100.00'))
        self.assertEqual(discount, Decimal('10.00'))
    
    def test_promotion_is_currently_active(self):
        promo = Promotion.objects.create(
            name='Flash Sale',
            promotion_type=self.promo_type,
            start_date=timezone.now() - timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=1),
            is_active=True,
            display_priority=10,
            created_by=self.user,
            discount_percentage=Decimal('10.00')  # Provide required discount field
        )
        self.assertTrue(promo.is_currently_active())

    def test_bundle_offer_str(self):
        promo = Promotion.objects.create(
            name='Bundle Sale',
            promotion_type=self.promo_type,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=10),
            created_by=self.user,
            discount_amount=Decimal('5.00')  # Provide required discount field
        )
        bundle = BundleOffer.objects.create(
            promotion=promo,
            buy_quantity=2,
            get_quantity=1,
            get_discount_percentage=Decimal('50.00')
        )
        self.assertEqual(str(bundle), f"Buy 2 Get 1 - {promo.name}")

    def test_promotion_usage_unique_together(self):
        promo = Promotion.objects.create(
            name='Sale',
            promotion_type=self.promo_type,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=10),
            created_by=self.user,
            discount_amount=Decimal('5.00'),  # Required field
        )
        order = Order.objects.create(
            user=self.user,
            shipping_address="123 Street",
            shipping_city="City",
            shipping_state="State",
            shipping_zip_code="12345",
            shipping_country="Country",
            email=self.user.email,
            subtotal=Decimal("10.00"),
            tax_amount=Decimal("1.00"),
            shipping_cost=Decimal("1.00"),
            discount_amount=Decimal("0.00"),
            total=Decimal("12.00"),
            status='PENDING',
            payment_status='PENDING'
        )
        usage1 = PromotionUsage.objects.create(
            promotion=promo,
            user=self.user,
            order=order,
            discount_amount=Decimal('5.00')
        )
        usage2 = PromotionUsage(
            promotion=promo,
            user=self.user,
            order=order,
            discount_amount=Decimal('5.00')
        )
        with self.assertRaises(IntegrityError):
            usage2.save()

    def test_coupon_usage_unique_together(self):
        coupon = Coupon.objects.create(
            code='SAVE20',
            discount_type='fixed',
            discount_value=Decimal('20.00'),
            valid_from=timezone.now(),
            valid_to=timezone.now() + timezone.timedelta(days=10),
            is_active=True,
            created_by=self.user
        )
        order = Order.objects.create(
            user=self.user,
            shipping_address="123 Street",
            shipping_city="City",
            shipping_state="State",
            shipping_zip_code="12345",
            shipping_country="Country",
            email=self.user.email,
            subtotal=Decimal("10.00"),
            tax_amount=Decimal("1.00"),
            shipping_cost=Decimal("1.00"),
            discount_amount=Decimal("0.00"),
            total=Decimal("12.00"),
            status='PENDING',
            payment_status='PENDING'
        )
        usage1 = CouponUsage.objects.create(
            coupon=coupon,
            user=self.user,
            order=order,
            discount_amount=Decimal('20.00')
        )
        usage2 = CouponUsage(
            coupon=coupon,
            user=self.user,
            order=order,
            discount_amount=Decimal('20.00')
        )
        with self.assertRaises(IntegrityError):
            usage2.save()

    def test_promo_banner_active_status(self):
        banner = PromoBanner.objects.create(
            title='Big Sale',
            description='Huge discounts',
            image='promo_banners/sale.jpg',
            is_active=True,
            display_order=1,
            start_date=timezone.now() - timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=10)
        )
        self.assertTrue(banner.is_currently_active())
