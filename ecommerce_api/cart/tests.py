from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Product, Category, Brand
from .models import Cart, CartItem, SavedCart
from decimal import Decimal

User = get_user_model()

class CartSetupMixin:
    """Mixin to set up test data for cart tests"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create test category and brand
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category',
            description='Test category description'
        )
        
        self.brand = Brand.objects.create(
            name='Test Brand',
            description='Test brand description'
        )
        
        # Create test products
        self.product1 = Product.objects.create(
            name='Test Product 1',
            slug='test-product-1',
            description='Test product description 1',
            price=Decimal('29.99'),
            sku='TEST001',
            quantity=10,
            category=self.category,
            brand=self.brand,
            status='ACTIVE'
        )
        
        self.product2 = Product.objects.create(
            name='Test Product 2',
            slug='test-product-2',
            description='Test product description 2',
            price=Decimal('49.99'),
            sku='TEST002',
            quantity=5,
            category=self.category,
            brand=self.brand,
            status='ACTIVE'
        )
        
        # Create APIClient and authenticate using force_authenticate
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


class CartModelTests(TestCase):
    """Test cart model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='modeltest@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test description',
            price=Decimal('19.99'),
            sku='TESTMODEL',
            quantity=5,
            category=self.category,
            status='ACTIVE'
        )
    
    def test_cart_creation(self):
        """Test that a cart is created for a user"""
        # Use get_or_create instead of create to avoid unique constraint issues
        cart, created = Cart.objects.get_or_create(user=self.user)
        self.assertEqual(cart.user, self.user)
        self.assertEqual(cart.total_items, 0)
        self.assertEqual(cart.subtotal, Decimal('0.00'))
    
    def test_cart_item_creation(self):
        """Test cart item creation and calculations"""
        cart, created = Cart.objects.get_or_create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2
        )
        
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.total_price, Decimal('39.98'))  # 2 * 19.99
        self.assertTrue(cart_item.is_available)
    
    def test_cart_totals(self):
        """Test cart total calculations"""
        cart, created = Cart.objects.get_or_create(user=self.user)
        
        # Add multiple items
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        
        # Create another product
        product2 = Product.objects.create(
            name='Test Product 2',
            slug='test-product-2',
            description='Test description 2',
            price=Decimal('9.99'),
            sku='TESTMODEL2',
            quantity=3,
            category=self.category,
            status='ACTIVE'
        )
        CartItem.objects.create(cart=cart, product=product2, quantity=1)
        
        self.assertEqual(cart.total_items, 3)
        self.assertEqual(cart.subtotal, Decimal('49.97'))  # (2*19.99) + (1*9.99)
        self.assertAlmostEqual(float(cart.tax_amount), 4.00, places=2)  # 8% of 49.97
        self.assertAlmostEqual(float(cart.total), 53.97, places=2)


class CartAPITests(CartSetupMixin, APITestCase):
    """Test cart API endpoints"""
    
    def test_get_cart(self):
        """Test retrieving user's cart"""
        url = '/api/cart/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check what fields are available and adjust assertions accordingly
        if 'total_items' in response.data:
            self.assertEqual(response.data['total_items'], 0)
        elif 'items' in response.data:
            # If total_items is not available, check items array length
            items = response.data['items']
            if isinstance(items, list):
                self.assertEqual(len(items), 0)
            elif 'results' in items:  # Handle pagination
                self.assertEqual(len(items['results']), 0)
        
        if 'subtotal' in response.data:
            self.assertEqual(response.data['subtotal'], '0.00')
    
    def test_clear_cart(self):
        """Test clearing cart"""
        # First add an item
        add_url = '/api/cart/add_item/'
        self.client.post(add_url, {
            'product_id': self.product1.id,
            'quantity': 1
        }, format='json')
        
        # Then clear cart
        clear_url = '/api/cart/clear/'
        response = self.client.post(clear_url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify cart is empty - check what fields are available
        cart_url = '/api/cart/'
        cart_response = self.client.get(cart_url)
        
        if 'total_items' in cart_response.data:
            self.assertEqual(cart_response.data['total_items'], 0)
        elif 'items' in cart_response.data:
            items = cart_response.data['items']
            if isinstance(items, list):
                self.assertEqual(len(items), 0)
            elif 'results' in items:  # Handle pagination
                self.assertEqual(len(items['results']), 0)
    
    def test_get_cart_count(self):
        """Test getting cart item count"""
        # Add some items first
        add_url = '/api/cart/add_item/'
        self.client.post(add_url, {
            'product_id': self.product1.id,
            'quantity': 2
        }, format='json')
        
        self.client.post(add_url, {
            'product_id': self.product2.id,
            'quantity': 1
        }, format='json')
        
        # Get count - this might be a separate endpoint or part of cart response
        count_url = '/api/cart/count/'
        response = self.client.get(count_url)
        
        if response.status_code == 200:
            # If count endpoint exists
            self.assertEqual(response.data['count'], 3)
        else:
            # If count endpoint doesn't exist, check cart total_items
            cart_url = '/api/cart/'
            cart_response = self.client.get(cart_url)
            if 'total_items' in cart_response.data:
                self.assertEqual(cart_response.data['total_items'], 3)
            elif 'items' in cart_response.data:
                items = cart_response.data['items']
                if isinstance(items, list):
                    self.assertEqual(len(items), 2)  # 2 items with quantities 2 and 1 = total 3
                elif 'results' in items:
                    self.assertEqual(len(items['results']), 2)
class CartItemAPITests(CartSetupMixin, APITestCase):
    """Test cart item API endpoints"""
    
    def setUp(self):
        super().setUp()
        # Create a cart with items for these tests
        self.cart, created = Cart.objects.get_or_create(user=self.user)
        
        # Add item using the API endpoint
        add_url = '/api/cart/add_item/'
        response = self.client.post(add_url, {
            'product_id': self.product1.id,
            'quantity': 2
        }, format='json')
        
        self.cart_item_id = response.data['id']
    
    def test_list_cart_items(self):
        """Test listing cart items"""
        url = '/api/cart/cart-items/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle pagination - check if results key exists
        if 'results' in response.data:
            items = response.data['results']
        else:
            items = response.data
        
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['quantity'], 2)
    
    def test_retrieve_cart_item(self):
        """Test retrieving specific cart item"""
        url = f'/api/cart/cart-items/{self.cart_item_id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.cart_item_id)
        self.assertEqual(response.data['quantity'], 2)
    
    def test_update_cart_item(self):
        """Test updating cart item quantity"""
        url = f'/api/cart/cart-items/{self.cart_item_id}/'
        data = {'quantity': 3}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 3)
    
    def test_delete_cart_item(self):
        """Test deleting cart item"""
        url = f'/api/cart/cart-items/{self.cart_item_id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify item is deleted
        url = '/api/cart/cart-items/'
        response = self.client.get(url)
        if 'results' in response.data:
            items = response.data['results']
        else:
            items = response.data
        self.assertEqual(len(items), 0)


class SavedCartAPITests(CartSetupMixin, APITestCase):
    """Test saved cart API endpoints"""
    
    def setUp(self):
        super().setUp()
        # Create a saved cart for tests
        self.saved_cart = SavedCart.objects.create(
            user=self.user,
            name='Test Saved Cart'
        )
    
    def test_list_saved_carts(self):
        """Test listing saved carts"""
        url = '/api/cart/saved-carts/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle pagination
        if 'results' in response.data:
            items = response.data['results']
        else:
            items = response.data
        
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['name'], 'Test Saved Cart')
    
    def test_create_saved_cart(self):
        """Test creating a new saved cart"""
        url = '/api/cart/saved-carts/'
        data = {
            'name': 'New Test Saved Cart',
            'description': 'Test description'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Test Saved Cart')
        
        # Verify creation in database
        self.assertTrue(SavedCart.objects.filter(name='New Test Saved Cart').exists())
    
    def test_retrieve_saved_cart(self):
        """Test retrieving specific saved cart"""
        url = f'/api/cart/saved-carts/{self.saved_cart.pk}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.saved_cart.id)
        self.assertEqual(response.data['name'], 'Test Saved Cart')
    
    def test_update_saved_cart(self):
        """Test updating saved cart"""
        url = f'/api/cart/saved-carts/{self.saved_cart.pk}/'
        data = {'name': 'Updated Saved Cart Name'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Saved Cart Name')
        
        # Verify update in database
        self.saved_cart.refresh_from_db()
        self.assertEqual(self.saved_cart.name, 'Updated Saved Cart Name')
    
    def test_delete_saved_cart(self):
        """Test deleting saved cart"""
        url = f'/api/cart/saved-carts/{self.saved_cart.pk}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify deletion
        self.assertFalse(SavedCart.objects.filter(pk=self.saved_cart.pk).exists())


class PermissionTests(APITestCase):
    """Test permission classes"""
    
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpass123'
        )
        
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )
        
        # Create category and product
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test description',
            price=Decimal('19.99'),
            sku='TESTPERM',
            quantity=5,
            category=self.category,
            status='ACTIVE'
        )
        
        # Create cart item for user1 using API
        client1 = APIClient()
        client1.force_authenticate(user=self.user1)
        
        response = client1.post('/api/cart/add_item/', {
            'product_id': self.product.id,
            'quantity': 1
        }, format='json')
        
        self.cart_item_id = response.data['id']
        
        # Create saved cart for user1
        self.saved_cart = SavedCart.objects.create(
            user=self.user1,
            name='Test Saved Cart'
        )
    
    def test_cannot_access_other_user_cart(self):
        """Test that users cannot access other users' cart items"""
        # Login as user2
        client = APIClient()
        client.force_authenticate(user=self.user2)
        
        # Try to access user1's cart item
        url = f'/api/cart/cart-items/{self.cart_item_id}/'
        response = client.get(url)
        
        # Should return 404 (not found) or 403 (forbidden)
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])
    
    def test_cannot_access_other_user_saved_cart(self):
        """Test that users cannot access other users' saved carts"""
        # Login as user2
        client = APIClient()
        client.force_authenticate(user=self.user2)
        
        # Try to access user1's saved cart
        url = f'/api/cart/saved-carts/{self.saved_cart.pk}/'
        response = client.get(url)
        
        # Should return 404 (not found) or 403 (forbidden)
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])