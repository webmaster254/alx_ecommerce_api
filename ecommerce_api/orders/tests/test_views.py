from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Product
from orders.models import Order, OrderItem, Payment, Shipping
from decimal import Decimal


User = get_user_model()


class OrdersViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@test.com', password='pass')
        self.staff_user = User.objects.create_user(email='staff@test.com', password='pass', is_staff=True)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.product = Product.objects.create(
            name='Sample', slug='sample', description='desc',
            price=Decimal('100'), sku='SKU001', quantity=10, status='ACTIVE'
        )

        self.order = Order.objects.create(
            user=self.user,
            shipping_address='123 Street',
            shipping_city='City',
            shipping_state='State',
            shipping_zip_code='12345',
            shipping_country='Country',
            email=self.user.email,
            subtotal=Decimal('200'),
            tax_amount=Decimal('16'),
            shipping_cost=Decimal('10'),
            discount_amount=Decimal('0'),
            total=Decimal('226'),
            status='PENDING',
            payment_status='PENDING'
        )
        self.item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=self.product.price,
            product_name=self.product.name,
            product_sku=self.product.sku
        )
        self.payment = Payment.objects.create(
            order=self.order,
            payment_method='CREDIT_CARD',
            amount=Decimal('226'),
            status='PENDING',
            transaction_id='TXN123456',
            payment_details={},
        )
        self.shipping = Shipping.objects.create(
            order=self.order,
            shipping_method='STANDARD',
            status='PENDING',
            shipping_cost=Decimal('10'),
            carrier='CarrierX',
            tracking_number='TRACK123',
        )

    def get_paginated_results(self, response):
        data = response.data
        if isinstance(data, dict) and 'results' in data:
            return data['results']
        return data

    def test_list_orders_user(self):
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_paginated_results(response)
        self.assertTrue(all(order['user'] == self.user.id for order in results))

    def test_list_orders_staff(self):
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_paginated_results(response)
        self.assertTrue(any(order['id'] == self.order.id for order in results))

    def test_retrieve_order(self):
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order.id)

    
    def test_cancel_order(self):
        url = reverse('order-cancel', kwargs={'pk': self.order.id})
        response = self.client.post(url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
        if response.status_code == status.HTTP_200_OK:
            self.order.refresh_from_db()
            self.assertEqual(self.order.status, 'CANCELLED')

    def test_list_order_items(self):
        url = reverse('order-items', kwargs={'pk': self.order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['product'], self.product.id)

    def test_list_payments(self):
        url = reverse('order-payments-list', kwargs={'order_pk': self.order.id})
        response = self.client.get(url)
        if response.status_code != status.HTTP_200_OK:
            print('Payments list response status:', response.status_code)
            print('Payments list response content:', response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_paginated_results(response)
        self.assertTrue(any(payment['id'] == self.payment.id for payment in results))

    def test_retrieve_payment(self):
        url = reverse('order-payments-detail', kwargs={'order_pk': self.order.id, 'pk': self.payment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.payment.id)

    def test_list_shipping(self):
        url = reverse('order-shipping-list', kwargs={'order_pk': self.order.id})
        response = self.client.get(url)
        if response.status_code != status.HTTP_200_OK:
            print('Shipping list response status:', response.status_code)
            print('Shipping list response content:', response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self.get_paginated_results(response)
        self.assertTrue(any(shipping['id'] == self.shipping.id for shipping in results))

    def test_retrieve_shipping(self):
        url = reverse('order-shipping-detail', kwargs={'order_pk': self.order.id, 'pk': self.shipping.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.shipping.id)
