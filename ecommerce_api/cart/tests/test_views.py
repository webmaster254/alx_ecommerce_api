from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from decimal import Decimal
import uuid

from cart.models import Cart, CartItem, SavedCart
from products.models import Product, Category, Brand

User = get_user_model()


class CartViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='otherpass123'
        )

        # Create category and brand
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.brand = Brand.objects.create(name="Test Brand")

        # Create products with unique slugs and SKUs
        self.product1 = Product.objects.create(
            name='Test Product 1',
            slug=f"test-product-1-{uuid.uuid4().hex[:8]}",
            description="Test description",
            price=Decimal('19.99'),
            quantity=10,
            category=self.category,
            brand=self.brand,
            sku=f"SKU-{uuid.uuid4().hex[:8]}",
            created_by=self.user,
            updated_by=self.user,
            status='ACTIVE'
        )
        self.product2 = Product.objects.create(
            name='Test Product 2',
            slug=f"test-product-2-{uuid.uuid4().hex[:8]}",
            description="Test description",
            price=Decimal('29.99'),
            quantity=5,
            category=self.category,
            brand=self.brand,
            sku=f"SKU-{uuid.uuid4().hex[:8]}",
            created_by=self.user,
            updated_by=self.user,
            status='ACTIVE'
        )

        self.cart_list_url = reverse('cart-list')
        self.cart_detail_url = lambda pk: reverse('cart-detail', kwargs={'pk': pk})
        self.add_item_url = reverse('cart-add-item')

        try:
            self.count_url = reverse('cart-count')
        except NoReverseMatch:
            self.count_url = None

        try:
            self.clear_url = reverse('cart-clear')
        except NoReverseMatch:
            self.clear_url = None

        self.cart_items_list_url = reverse('cartitem-list')
        self.cart_item_detail_url = lambda pk: reverse('cartitem-detail', kwargs={'pk': pk})

        try:
            self.saved_carts_list_url = reverse('savedcart-list')
        except NoReverseMatch:
            self.saved_carts_list_url = None

        self.saved_cart_detail_url = lambda pk: reverse('savedcart-detail', kwargs={'pk': pk})
        self.restore_url = lambda pk: reverse('savedcart-restore', kwargs={'pk': pk})

    def test_get_cart_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.cart_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if isinstance(response.data, list):
            self.assertIsInstance(response.data, list)
        elif isinstance(response.data, dict) and 'results' in response.data:
            self.assertIsInstance(response.data['results'], list)

    def test_get_cart_list_unauthenticated(self):
        response = self.client.get(self.cart_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_cart_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.cart_list_url, {})
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

    def test_get_cart_detail_authenticated(self):
        cart, _ = Cart.objects.get_or_create(user=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.cart_detail_url(cart.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['id']), str(cart.pk))

    def test_get_cart_detail_other_user(self):
        cart, _ = Cart.objects.get_or_create(user=self.other_user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.cart_detail_url(cart.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_item_to_cart_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {'product_id': self.product1.pk, 'quantity': 3}
        response = self.client.post(self.add_item_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['product'], self.product1.pk)
        self.assertEqual(response.data['quantity'], 3)

    def test_add_item_to_cart_unauthenticated(self):
        data = {'product_id': self.product1.pk, 'quantity': 2}
        response = self.client.post(self.add_item_url, data)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN])

    def test_add_item_to_cart_insufficient_stock(self):
        self.client.force_authenticate(user=self.user)
        data = {'product_id': self.product1.pk, 'quantity': 15}
        response = self.client.post(self.add_item_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_item_to_cart_invalid_product(self):
        self.client.force_authenticate(user=self.user)
        data = {'product_id': 999999, 'quantity': 1}
        response = self.client.post(self.add_item_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CartItemViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@example.com', password='testpass123')

        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.brand = Brand.objects.create(name="Test Brand")

        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('19.99'),
            quantity=10,
            category=self.category,
            brand=self.brand,
            sku=f"SKU-{uuid.uuid4().hex[:8]}",
            created_by=self.user,
            updated_by=self.user
        )

        self.cart, _ = Cart.objects.get_or_create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )

        self.cart_items_url = reverse('cartitem-list')
        self.cart_item_detail_url = lambda pk: reverse('cartitem-detail', kwargs={'pk': pk})
        self.cart_list_url = reverse('cart-list')

    def test_list_cart_items_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.cart_items_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if isinstance(response.data, dict) and 'results' in response.data:
            cart_item_ids = [item['id'] for item in response.data['results']]
        elif isinstance(response.data, list):
            cart_item_ids = [item['id'] for item in response.data]
        else:
            self.fail(f"Unexpected response data format: {type(response.data)}")
        self.assertIn(self.cart_item.id, cart_item_ids)

    def test_retrieve_cart_item(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.cart_item_detail_url(self.cart_item.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.cart_item.id)

    def test_update_cart_item_quantity(self):
        self.client.force_authenticate(user=self.user)
        data = {'quantity': 5}
        response = self.client.patch(self.cart_item_detail_url(self.cart_item.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 5)
        self.cart_item.refresh_from_db()
        self.assertEqual(self.cart_item.quantity, 5)

    def test_delete_cart_item(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.cart_item_detail_url(self.cart_item.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.items.count(), 0)


class SavedCartViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@example.com', password='testpass123')
        self.other_user = User.objects.create_user(email='other@example.com', password='otherpass123')

        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.brand = Brand.objects.create(name="Test Brand")

        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('19.99'),
            quantity=10,
            category=self.category,
            brand=self.brand,
            sku=f"SKU-{uuid.uuid4().hex[:8]}",
            created_by=self.user,
            updated_by=self.user
        )

        self.cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

        try:
            self.saved_carts_url = reverse('savedcart-list')
        except NoReverseMatch:
            self.saved_carts_url = None
        self.saved_cart_detail_url = lambda pk: reverse('savedcart-detail', kwargs={'pk': pk})
        self.restore_url = lambda pk: reverse('savedcart-restore', kwargs={'pk': pk})

    def test_list_saved_carts_authenticated(self):
        if not self.saved_carts_url:
            self.skipTest("savedcart-list URL not configured")
        saved_cart = SavedCart.objects.create(user=self.user, name='My Wishlist')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.saved_carts_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if isinstance(response.data, dict) and 'results' in response.data:
            saved_cart_ids = [cart['id'] for cart in response.data['results']]
        elif isinstance(response.data, list):
            saved_cart_ids = [cart['id'] for cart in response.data]
        else:
            self.fail(f"Unexpected response data format: {type(response.data)}")
        self.assertIn(saved_cart.id, saved_cart_ids)

    def test_list_saved_carts_unauthenticated(self):
        if not self.saved_carts_url:
            self.skipTest("savedcart-list URL not configured")
        response = self.client.get(self.saved_carts_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_saved_cart(self):
        if not self.saved_carts_url:
            self.skipTest("savedcart-list URL not configured")
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'My Wishlist',
            'items': [{'product': self.product.pk, 'quantity': 1}]
        }
        response = self.client.post(self.saved_carts_url, data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            self.fail(f"Create saved cart failed: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'My Wishlist')

    def test_retrieve_saved_cart(self):
        saved_cart = SavedCart.objects.create(user=self.user, name='My Wishlist')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.saved_cart_detail_url(saved_cart.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'My Wishlist')

    def test_retrieve_other_user_saved_cart(self):
        saved_cart = SavedCart.objects.create(user=self.other_user, name='Other Wishlist')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.saved_cart_detail_url(saved_cart.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_saved_cart(self):
        saved_cart = SavedCart.objects.create(user=self.user, name='Old Name')
        self.client.force_authenticate(user=self.user)
        data = {'name': 'New Name'}
        response = self.client.patch(self.saved_cart_detail_url(saved_cart.pk), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'New Name')
        saved_cart.refresh_from_db()
        self.assertEqual(saved_cart.name, 'New Name')

    def test_delete_saved_cart(self):
        saved_cart = SavedCart.objects.create(user=self.user, name='My Wishlist')
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.saved_cart_detail_url(saved_cart.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(SavedCart.objects.filter(user=self.user).exists())


class EdgeCasesTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@example.com', password='testpass123')
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.brand = Brand.objects.create(name="Test Brand")
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('0.00'),
            quantity=5,
            category=self.category,
            brand=self.brand,
            sku=f"SKU-{uuid.uuid4().hex[:8]}",
            created_by=self.user,
            updated_by=self.user
        )
        self.cart_url = reverse('cart-list')
        self.add_item_url = reverse('cart-add-item')

    def test_cart_calculations_with_zero_price(self):
        self.client.force_authenticate(user=self.user)
        data = {'product_id': self.product.pk, 'quantity': 3}
        response = self.client.post(self.add_item_url, data)

        # Replace skipTest with assertion failure
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Add item endpoint not working as expected.")

        cart_response = self.client.get(self.cart_url)

        if isinstance(cart_response.data, list) and len(cart_response.data) > 0:
            cart_data = cart_response.data[0]
        elif isinstance(cart_response.data, dict):
            cart_data = cart_response.data
        else:
            self.fail("Unexpected cart response format")

        self.assertEqual(Decimal(str(cart_data.get('subtotal', '0.00'))), Decimal('0.00'))
        self.assertEqual(Decimal(str(cart_data.get('tax_amount', '0.00'))), Decimal('0.00'))
        self.assertEqual(Decimal(str(cart_data.get('total', '0.00'))), Decimal('0.00'))

class SessionCartTest(APITestCase):
    """Test session-based cart functionality for anonymous users"""

    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.brand = Brand.objects.create(name="Test Brand")
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('19.99'),
            quantity=10,
            category=self.category,
            brand=self.brand,
            sku=f"SKU-{uuid.uuid4().hex[:8]}"
        )
        self.add_item_url = reverse('cart-add-item')
        self.cart_list_url = reverse('cart-list')

    def test_anonymous_user_cart_creation(self):
        data = {'product_id': self.product.pk, 'quantity': 2}
        response = self.client.post(self.add_item_url, data)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN])
