from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from products.models import Product, Category, Brand
from cart.models import Cart, CartItem

User = get_user_model()

class CartModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass123')

        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.brand = Brand.objects.create(name="Test Brand")

        self.product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            description="A test product",
            price=Decimal('10.00'),
            quantity=5,
            sku="SKU123",
            category=self.category,
            brand=self.brand,
            status='ACTIVE',
            created_by=self.user,
            updated_by=self.user,
        )

        self.product2 = Product.objects.create(
            name="Test Product 2",
            slug="test-product-2",
            description="Second test product",
            price=Decimal('20.00'),
            quantity=3,
            sku="SKU124",
            category=self.category,
            brand=self.brand,
            status='ACTIVE',
            created_by=self.user,
            updated_by=self.user,
        )

        # Use get_or_create to avoid UNIQUE constraint error if Cart already exists
        self.cart, created = Cart.objects.get_or_create(user=self.user)

    def test_create_cart_and_cart_item(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

        self.assertEqual(str(self.cart), f"Cart for {self.user.email}")
        self.assertEqual(self.cart.total_items, 2)
        self.assertEqual(self.cart.subtotal, Decimal('20.00'))
        self.assertEqual(self.cart.tax_amount, Decimal('1.60'))
        self.assertEqual(self.cart.total, Decimal('21.60'))

        self.assertEqual(str(item), "2 x Test Product")
        self.assertTrue(item.is_available)
        self.assertEqual(item.total_price, Decimal('20.00'))

    def test_cart_item_quantity_limits(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=10)
        self.assertEqual(item.quantity, 5)  # quantity capped at product stock

    def test_cart_clear_method(self):
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=1)
        self.assertEqual(self.cart.items.count(), 2)

        self.cart.clear()
        self.assertEqual(self.cart.items.count(), 0)

    def test_merge_with_session_cart(self):
        user_cart = self.cart
        CartItem.objects.create(cart=user_cart, product=self.product, quantity=1)

        session_cart = Cart.objects.create(session_key='abc123')
        CartItem.objects.create(cart=session_cart, product=self.product, quantity=2)
        CartItem.objects.create(cart=session_cart, product=self.product2, quantity=1)

        user_cart.merge_with_session_cart(session_cart)

        with self.assertRaises(Cart.DoesNotExist):
            Cart.objects.get(pk=session_cart.pk)

        user_item = user_cart.items.get(product=self.product)
        user_item2 = user_cart.items.get(product=self.product2)

        self.assertEqual(user_item.quantity, 3)
        self.assertEqual(user_item2.quantity, 1)

    def test_cart_str_for_guest_and_anonymous(self):
        guest_cart = Cart.objects.create(guest_email='guest@example.com')
        self.assertEqual(str(guest_cart), "Guest cart for guest@example.com")

        anon_cart = Cart.objects.create(session_key='sess123')
        self.assertEqual(str(anon_cart), "Anonymous cart (sess123)")
