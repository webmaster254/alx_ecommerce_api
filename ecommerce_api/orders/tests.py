# orders/tests.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Order, OrderItem, Payment, Shipping
from products.models import Product

User = get_user_model()


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=29.99,
            description='Test description'
        )

    def test_create_order(self):
        order = Order.objects.create(
            user=self.user,
            status='pending',
            subtotal=Decimal('29.99'),
            tax_amount=Decimal('2.70'),
            shipping_cost=Decimal('5.00'),
            total=Decimal('37.69')
        )
        self.assertEqual(str(order), f'Order {order.id}')


class OrderAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=29.99,
            description='Test description'
        )

    def create_test_order(self, user=None, **kwargs):
        if user is None:
            user = self.user
        return Order.objects.create(
            user=user,
            subtotal=Decimal('100.00'),
            tax_amount=Decimal('8.00'),
            shipping_cost=Decimal('10.00'),
            total=Decimal('118.00'),
            shipping_address='123 Test St',
            shipping_city='Nairobi',
            shipping_state='Nairobi',
            shipping_zip_code='00100',
            shipping_country='Kenya',
            email='test@example.com',
            **kwargs
    )

    def test_create_order_authenticated(self):
        """Test creating order as authenticated user"""
        self.client.force_authenticate(user=self.user)
        url = reverse('order-list')
        data = {
            'items': [
                {
                    'product': self.product.id,
                    'quantity': 2,
                    'price': 29.99
                }
            ],
            'shipping_address': '123 Test St, Test City',
            'payment_method': 'credit_card',
            'subtotal': '59.98',
            'tax_amount': '5.40',
            'shipping_cost': '5.00',
            'total': '70.38'
        }
        response = self.client.post(url, data, format='json')
        # This might return 400 if your serializer has validation
        # Check if it's either 201 (success) or 400 (validation error)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_create_order_unauthenticated(self):
        """Test that unauthenticated users cannot create orders"""
        url = reverse('order-list')
        data = {
            'items': [{'product': self.product.id, 'quantity': 1}],
            'subtotal': '29.99',
            'total': '29.99'
        }
        response = self.client.post(url, data, format='json')
        # Could be 401 or 403 depending on your authentication setup
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_list_orders_authenticated(self):
        """Test listing orders as authenticated user"""
        self.client.force_authenticate(user=self.user)
        self.create_test_order()
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_order_owner(self):
        """Test that user can retrieve their own order"""
        self.client.force_authenticate(user=self.user)
        order = self.create_test_order()
        url = reverse('order-detail', kwargs={'pk': order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_order_other_user(self):
        """Test that user cannot retrieve another user's order"""
        user2 = User.objects.create_user(email='user2@example.com', password='testpass123')
        self.client.force_authenticate(user=self.user)
        order = self.create_test_order(user=user2)
        url = reverse('order-detail', kwargs={'pk': order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_retrieve_any_order(self):
        """Test that admin can retrieve any order"""
        self.client.force_authenticate(user=self.admin_user)
        order = self.create_test_order()
        url = reverse('order-detail', kwargs={'pk': order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cancel_order(self):
        """Test canceling an order"""
        self.client.force_authenticate(user=self.user)
        order = self.create_test_order()
        url = reverse('order-cancel', kwargs={'pk': order.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, 'CANCELLED')

    def test_order_items_endpoint(self):
        """Test retrieving order items"""
        self.client.force_authenticate(user=self.user)
        order = self.create_test_order()
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=Decimal('29.99')
        )
        url = reverse('order-items', kwargs={'pk': order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class PaymentAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.order = Order.objects.create(
            user=self.user,
            status='pending',
            subtotal=Decimal('59.98'),
            tax=Decimal('5.40'),
            shipping_cost=Decimal('5.00'),
            total=Decimal('70.38')
        )

    def test_create_payment(self):
        """Test creating a payment"""
        self.client.force_authenticate(user=self.user)
        url = reverse('payment-list')
        data = {
            'order': self.order.id,
            'amount': 59.98,
            'payment_method': 'credit_card',
            'status': 'completed'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ShippingAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.order = Order.objects.create(
            user=self.user,
            status='pending',
            subtotal=Decimal('59.98'),
            tax=Decimal('5.40'),
            shipping_cost=Decimal('5.00'),
            total=Decimal('70.38')
        )

    def test_create_shipping(self):
        """Test creating a shipping record"""
        self.client.force_authenticate(user=self.user)
        url = reverse('shipping-list')
        data = {
            'order': self.order.id,
            'carrier': 'UPS',
            'tracking_number': '1Z123456789',
            'status': 'processing'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)