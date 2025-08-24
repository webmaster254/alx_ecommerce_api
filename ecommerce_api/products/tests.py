from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Product, Category, Brand, ProductReview, Wishlist

User = get_user_model()

class ProductSetupMixin:
    """Mixin to set up test data for product tests"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
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
            price=99.99,
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
            price=149.99,
            sku='TEST002',
            quantity=5,
            category=self.category,
            status='ACTIVE'
        )
        
        # Create APIClient and authenticate
        self.client = APIClient()


class ProductModelTests(TestCase):
    """Test product model functionality"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        self.brand = Brand.objects.create(
            name='Test Brand',
            description='Test brand description'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test description',
            price=99.99,
            sku='TESTMODEL',
            quantity=5,
            category=self.category,
            brand=self.brand,
            status='ACTIVE'
        )
    
    def test_product_creation(self):
        """Test that a product is created correctly"""
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.slug, 'test-product')
        self.assertEqual(self.product.price, 99.99)
        self.assertEqual(self.product.quantity, 5)
        self.assertEqual(self.product.status, 'ACTIVE')
    
    def test_product_str_method(self):
        """Test product string representation"""
        self.assertEqual(str(self.product), 'Test Product')
    
    def test_product_is_in_stock(self):
        """Test product stock status"""
        self.assertTrue(self.product.is_in_stock)
        
        # Test out of stock
        self.product.quantity = 0
        self.assertFalse(self.product.is_in_stock)
    
    def test_product_discount_percentage(self):
        """Test product discount calculation"""
        # Test without compare price
        self.assertEqual(self.product.discount_percentage, 0)
        
        # Test with compare price
        self.product.compare_price = 129.99
        self.assertGreater(self.product.discount_percentage, 0)


class ProductAPITests(ProductSetupMixin, APITestCase):
    """Test product API endpoints"""
    
    def test_debug_product_endpoint(self):
        """Debug the product endpoint to see what's happening"""
        url = '/api/products/'
        
        # Test OPTIONS to see what methods are allowed
        print(f"Testing OPTIONS on {url}")
        response = self.client.options(url)
        print(f"OPTIONS {url}: {response.status_code}")
        if response.status_code == 200:
            print(f"Allowed methods: {response.data}")
        
        # Test POST as admin
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'name': 'Test Product',
            'slug': 'test-product-debug',
            'description': 'Test description',
            'price': 99.99,
            'sku': 'DEBUG001',
            'quantity': 5,
            'category': self.category.id,
            'status': 'DRAFT'
        }
        
        print(f"Testing POST on {url} with data: {data}")
        response = self.client.post(url, data, format='json')
        print(f"POST {url}: {response.status_code}")
        if response.status_code != 200:
            print(f"Response data: {response.data}")
    


class CategoryAPITests(ProductSetupMixin, APITestCase):
    """Test category API endpoints"""
    
    def test_list_categories(self):
        """Test listing all categories"""
        self.client.force_authenticate(user=self.user)
        url = '/api/products/categories/'
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_retrieve_category(self):
        """Test retrieving specific category"""
        self.client.force_authenticate(user=self.user)
        url = f'/api/products/categories/{self.category.id}/'
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Category')


class BrandAPITests(ProductSetupMixin, APITestCase):
    """Test brand API endpoints"""
    
    def test_list_brands(self):
        """Test listing all brands"""
        self.client.force_authenticate(user=self.user)
        url = '/api/products/brands/'
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_retrieve_brand(self):
        """Test retrieving specific brand"""
        self.client.force_authenticate(user=self.user)
        url = f'/api/products/brands/{self.brand.id}/'
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Brand')


class ReviewAPITests(ProductSetupMixin, APITestCase):
    """Test review API endpoints"""
    
    def test_create_review(self):
        """Test creating a product review"""
        self.client.force_authenticate(user=self.user)
        url = '/api/products/reviews/'
        data = {
            'product': self.product1.id,
            'rating': 5,
            'title': 'Excellent product',
            'comment': 'This product exceeded my expectations!'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)
    
    def test_list_reviews(self):
        """Test listing product reviews"""
        self.client.force_authenticate(user=self.user)
        url = '/api/products/reviews/'
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class WishlistAPITests(ProductSetupMixin, APITestCase):
    """Test wishlist API endpoints"""
    
    def test_get_wishlist(self):
        """Test getting user wishlist"""
        self.client.force_authenticate(user=self.user)
        url = '/api/products/wishlist/'
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should be empty initially
    
    def test_add_to_wishlist(self):
        """Test adding product to wishlist"""
        self.client.force_authenticate(user=self.user)
        url = '/api/products/wishlist/'
        data = {'product': self.product1.id}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)