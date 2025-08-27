from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import datetime, timedelta
from products.models import Product
from orders.models import Order, OrderItem, Payment, Shipping

User = get_user_model()

class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@test.com', password='pass')
        self.product = Product.objects.create(
            name='Sample Product', slug='sample-product', description='desc',
            price=Decimal('50.00'), sku='SKU123', quantity=100, status='ACTIVE'
        )
        self.order = Order.objects.create(
            user=self.user,
            shipping_address='123 Street',
            shipping_city='City',
            shipping_state='State',
            shipping_zip_code='12345',
            shipping_country='Country',
            email='user@test.com',
            subtotal=Decimal('0.00'),
            tax_amount=Decimal('0.00'),
            shipping_cost=Decimal('0.00'),
            total=Decimal('0.00'),
            status='PENDING',
            payment_status='PENDING'
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=self.product.price,
            product_name=self.product.name,
            product_sku=self.product.sku
        )

    def test_order_str(self):
        self.assertEqual(str(self.order), f"Order #{self.order.order_number} - {self.user.email}")

    def test_order_item_str(self):
        self.assertEqual(str(self.order_item), f"2 x {self.product.name} (Order #{self.order.order_number})")

    def test_order_item_save_sets_product_details(self):
        order_item = OrderItem(order=self.order, product=self.product, quantity=3)
        order_item.save()
        self.assertEqual(order_item.product_name, self.product.name)
        self.assertEqual(order_item.product_sku, self.product.sku)
        self.assertEqual(order_item.price, self.product.price)

    def test_calculate_totals(self):
        self.order.calculate_totals()
        expected_subtotal = self.order_item.total_price
        expected_tax = expected_subtotal * Decimal('0.08')
        expected_shipping = Decimal('10.00')
        expected_total = expected_subtotal + expected_tax + expected_shipping - self.order.discount_amount
        self.assertEqual(self.order.subtotal, expected_subtotal)
        self.assertEqual(self.order.tax_amount, expected_tax)
        self.assertEqual(self.order.shipping_cost, expected_shipping)
        self.assertEqual(self.order.total, expected_total)

    def test_item_count_property(self):
        self.assertEqual(self.order.item_count, 1)
        # Add another item
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=self.product.price,
            product_name=self.product.name,
            product_sku=self.product.sku
        )
        self.assertEqual(self.order.item_count, 2)

    def test_can_be_cancelled_property(self):
        self.order.status = 'PENDING'
        self.assertTrue(self.order.can_be_cancelled)
        self.order.status = 'PROCESSING'
        self.assertTrue(self.order.can_be_cancelled)
        self.order.status = 'SHIPPED'
        self.assertFalse(self.order.can_be_cancelled)

    def test_reduce_stock_updates_product_quantity(self):
        initial_quantity = self.product.quantity
        self.order.status = 'SHIPPED'
        self.order.save()  # This calls update_stock
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, initial_quantity - self.order_item.quantity)

class PaymentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@test.com', password='pass')
        self.order = Order.objects.create(
            user=self.user,
            shipping_address='123 Street',
            shipping_city='City',
            shipping_state='State',
            shipping_zip_code='12345',
            shipping_country='Country',
            email='user@test.com',
            subtotal=Decimal('100.00'),
            tax_amount=Decimal('8.00'),
            shipping_cost=Decimal('10.00'),
            total=Decimal('118.00'),
        )
        self.payment = Payment.objects.create(
            order=self.order,
            payment_method='CREDIT_CARD',
            amount=Decimal('118.00'),
            status='PENDING',
            transaction_id='TX12345678',
            payment_details={'transaction': 'details'}
        )

    def test_payment_str(self):
        self.assertEqual(str(self.payment), f"Payment #{self.payment.transaction_id} - {self.payment.amount}")

class ShippingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@test.com', password='pass')
        self.order = Order.objects.create(
            user=self.user,
            shipping_address='123 Street',
            shipping_city='City',
            shipping_state='State',
            shipping_zip_code='12345',
            shipping_country='Country',
            email='user@test.com',
            subtotal=Decimal('100.00'),
            tax_amount=Decimal('8.00'),
            shipping_cost=Decimal('10.00'),
            total=Decimal('118.00'),
        )
        self.shipping = Shipping.objects.create(
            order=self.order,
            shipping_method='STANDARD',
            tracking_number='TRACK123',
            carrier='CarrierX',
            status='PENDING',
            shipping_cost=Decimal('10.00')
        )

    def test_shipping_str(self):
        self.assertEqual(str(self.shipping), f"Shipping for Order #{self.order.order_number}")
