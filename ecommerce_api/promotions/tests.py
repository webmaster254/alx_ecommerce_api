# promotions/tests.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import (
    Promotion, PromotionType, Coupon, CouponUsage,
    BundleOffer, PromoBanner, PromotionUsage
)
from products.models import Product

User = get_user_model()


class PromotionModelTest(TestCase):
    def setUp(self):
        self.promo_type = PromotionType.objects.create(
            name='Discount',
            description='Percentage discount'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=100.00
        )

    def test_create_promotion(self):
        promotion = Promotion.objects.create(
            name='Summer Sale',
            promotion_type=self.promo_type,
            discount_value=20,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True
        )
        promotion.applicable_products.add(self.product)
        self.assertEqual(str(promotion), 'Summer Sale')


class CouponModelTest(TestCase):
    def test_create_coupon(self):
        coupon = Coupon.objects.create(
            code='SUMMER2024',
            discount_type='percentage',
            discount_value=15,
            min_order_amount=50,
            max_discount=25,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            usage_limit=100,
            is_active=True
        )
        self.assertEqual(str(coupon), 'SUMMER2024')


class PromotionAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.promo_type = PromotionType.objects.create(
            name='Discount',
            description='Percentage discount'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=100.00
        )

    def test_create_promotion_admin(self):
        """Test creating promotion as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('promotion-list')
        data = {
            'name': 'Winter Sale',
            'promotion_type': self.promo_type.id,
            'discount_value': 25,
            'start_date': timezone.now().isoformat(),
            'end_date': (timezone.now() + timedelta(days=30)).isoformat(),
            'is_active': True,
            'applicable_products': [self.product.id]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_promotion_non_admin(self):
        """Test that non-admin users cannot create promotions"""
        self.client.force_authenticate(user=self.user)
        url = reverse('promotion-list')
        data = {'name': 'Test Promotion', 'discount_value': 10}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_promotions_authenticated(self):
        """Test listing promotions as authenticated user"""
        self.client.force_authenticate(user=self.user)
        Promotion.objects.create(
            name='Test Promotion',
            promotion_type=self.promo_type,
            discount_value=10,
            is_active=True
        )
        url = reverse('promotion-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_active_promotions(self):
        """Test retrieving active promotions"""
        self.client.force_authenticate(user=self.user)
        Promotion.objects.create(
            name='Active Promotion',
            promotion_type=self.promo_type,
            discount_value=15,
            is_active=True
        )
        Promotion.objects.create(
            name='Inactive Promotion',
            promotion_type=self.promo_type,
            discount_value=10,
            is_active=False
        )
        url = reverse('promotion-active')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Active Promotion')

    def test_get_applicable_products(self):
        """Test retrieving products applicable to a promotion"""
        self.client.force_authenticate(user=self.user)
        promotion = Promotion.objects.create(
            name='Test Promotion',
            promotion_type=self.promo_type,
            discount_value=10,
            is_active=True
        )
        promotion.applicable_products.add(self.product)
        url = reverse('promotion-applicable-products', kwargs={'pk': promotion.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class CouponAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.coupon = Coupon.objects.create(
            code='TEST2024',
            discount_type='percentage',
            discount_value=10,
            min_order_amount=0,
            is_active=True
        )

    def test_validate_coupon_valid(self):
        """Test validating a valid coupon"""
        self.client.force_authenticate(user=self.user)
        url = reverse('coupon-validate')
        data = {
            'code': 'TEST2024',
            'order_amount': 100.00
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valid'])

    def test_validate_coupon_invalid(self):
        """Test validating an invalid coupon"""
        self.client.force_authenticate(user=self.user)
        url = reverse('coupon-validate')
        data = {
            'code': 'INVALID',
            'order_amount': 100.00
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['valid'])

    def test_validate_coupon_min_order(self):
        """Test coupon validation with minimum order amount"""
        coupon = Coupon.objects.create(
            code='MINORDER',
            discount_type='percentage',
            discount_value=10,
            min_order_amount=200,
            is_active=True
        )
        self.client.force_authenticate(user=self.user)
        url = reverse('coupon-validate')
        data = {
            'code': 'MINORDER',
            'order_amount': 100.00  # Below minimum
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['valid'])

    def test_create_coupon_admin(self):
        """Test creating coupon as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('coupon-list')
        data = {
            'code': 'NEW2024',
            'discount_type': 'percentage',
            'discount_value': 15,
            'min_order_amount': 0,
            'is_active': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class BundleOfferAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.product1 = Product.objects.create(name='Product 1', price=50.00)
        self.product2 = Product.objects.create(name='Product 2', price=30.00)

    def test_create_bundle_offer(self):
        """Test creating bundle offer as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('bundle-offer-list')
        data = {
            'name': 'Test Bundle',
            'description': 'Test bundle offer',
            'discount_percentage': 20,
            'products': [self.product1.id, self.product2.id],
            'is_active': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class PublicPromotionAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.product = Product.objects.create(name='Test Product', price=100.00)
        self.promo_type = PromotionType.objects.create(name='Discount')
        
        # Create active promotion
        self.promotion = Promotion.objects.create(
            name='Active Promotion',
            promotion_type=self.promo_type,
            discount_value=15,
            is_active=True
        )
        self.promotion.applicable_products.add(self.product)

    def test_get_all_active_public_promotions(self):
        """Test retrieving all active promotions (public endpoint)"""
        url = reverse('public-promotions-all-active')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_promotions_for_product(self):
        """Test retrieving promotions for a specific product"""
        url = reverse('public-promotions-for-product', kwargs={'product_id': self.product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class PromoBannerAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )

    def test_get_active_banners(self):
        """Test retrieving active promo banners"""
        PromoBanner.objects.create(
            title='Active Banner',
            description='Test banner',
            is_active=True
        )
        PromoBanner.objects.create(
            title='Inactive Banner',
            description='Test banner',
            is_active=False
        )
        url = reverse('promo-banner-active')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Active Banner')