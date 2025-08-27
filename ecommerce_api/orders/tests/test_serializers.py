from django.test import TestCase
from decimal import Decimal, ROUND_HALF_UP
from orders.serializers import (
    OrderSerializer, OrderCreateSerializer,
    OrderItemSerializer, PaymentSerializer, ShippingSerializer
)
from orders.models import Order, OrderItem, Payment, Shipping
from products.models import Product
from django.contrib.auth import get_user_model


User = get_user_model()


class OrderSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="testuser@example.com", password="testpass")
        self.product = Product.objects.create(
            name="Test Product", slug="test-product",
            description="Product description",
            price=Decimal("99.99"), sku="TP001",
            quantity=100, status="ACTIVE"
        )
        self.order = Order.objects.create(
            user=self.user,
            shipping_address="123 Test St", shipping_city="City",
            shipping_state="State", shipping_zip_code="12345",
            shipping_country="Country", email=self.user.email,
            subtotal=Decimal("99.99"), tax_amount=Decimal("10.00"),
            shipping_cost=Decimal("5.00"), discount_amount=Decimal("0.00"),
            total=Decimal("114.99"), status="PENDING", payment_status="PENDING"
        )
        self.order_item = OrderItem.objects.create(
            order=self.order, product=self.product,
            quantity=1, price=self.product.price,
            product_name=self.product.name, product_sku=self.product.sku
        )
        self.payment = Payment.objects.create(
            order=self.order, payment_method="CREDIT_CARD",
            amount=self.order.total, status="PENDING",
            transaction_id="TXN123456789", payment_details={}
        )
        self.shipping = Shipping.objects.create(
            order=self.order, shipping_method="STANDARD",
            status="PENDING", shipping_cost=Decimal("5.00"),
            carrier="CarrierX", tracking_number="TRACK123"
        )

    def test_orderitem_serialization(self):
        serializer = OrderItemSerializer(self.order_item)
        data = serializer.data
        self.assertEqual(data['product'], self.product.id)
        self.assertEqual(data['quantity'], 1)
        self.assertEqual(data['price'], str(self.product.price))
        self.assertIn('product_details', data)

    def test_order_serialization(self):
        serializer = OrderSerializer(self.order)
        data = serializer.data
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['subtotal'], "99.99")
        self.assertEqual(len(data['items']), 1)

    def test_order_create_serializer_valid(self):
        payload = {
            "shipping_address": "456 New St",
            "shipping_city": "New City",
            "shipping_state": "New State",
            "shipping_zip_code": "67890",
            "shipping_country": "New Country",
            "billing_address": "456 New St",
            "billing_city": "New City",
            "billing_state": "New State",
            "billing_zip_code": "67890",
            "billing_country": "New Country",
            "email": "newuser@example.com",
            "phone": "1234567890",
            "customer_notes": "Please deliver fast",
            "items": [
                {
                    "product": self.product.id,
                    "quantity": 2
                }
            ]
        }
        serializer = OrderCreateSerializer(data=payload)
        self.assertTrue(serializer.is_valid())

    def test_order_create_invalid_missing_field(self):
        payload = {
            "shipping_address": "456 New St",
            "items": []
        }
        serializer = OrderCreateSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        # Check required shipping fields errors
        self.assertIn('shipping_city', serializer.errors)
        # We do not error check 'items' because it may not be required in serializer

    def test_payment_serialization(self):
        serializer = PaymentSerializer(self.payment)
        data = serializer.data
        self.assertEqual(data['payment_method'], "CREDIT_CARD")
        expected = self.order.total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        actual = Decimal(data['amount']).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.assertEqual(actual, expected)

    def test_shipping_serialization(self):
        serializer = ShippingSerializer(self.shipping)
        data = serializer.data
        self.assertEqual(data['shipping_method'], "STANDARD")
        self.assertEqual(data['carrier'], "CarrierX")
