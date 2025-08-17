from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from products.models import Product, Category
from users.models import CustomUser

class ProductFilterTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.electronics = Category.objects.create(
            name='Electronics',
            description='Electronic items'
        )
        self.clothing = Category.objects.create(
            name='Clothing',
            description='Apparel items'
        )
        
        # Create test products
        Product.objects.create(
            name='Laptop',
            description='High performance laptop',
            price=999.99,
            category=self.electronics,
            stock_quantity=10,
            created_by=self.user
        )
        Product.objects.create(
            name='T-Shirt',
            description='Cotton t-shirt',
            price=19.99,
            category=self.clothing,
            stock_quantity=0,  # Out of stock
            created_by=self.user
        )
        Product.objects.create(
            name='Smartphone',
            description='Latest smartphone',
            price=699.99,
            category=self.electronics,
            stock_quantity=5,
            created_by=self.user
        )

    def test_category_filter(self):
        url = reverse('product-list')
        response = self.client.get(url, {'category': 'Electronics'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        for product in response.data['results']:
            self.assertEqual(product['category']['name'], 'Electronics')

    def test_price_range_filter(self):
        url = reverse('product-list')
        response = self.client.get(url, {'min_price': 500, 'max_price': 800})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Smartphone')

    def test_in_stock_filter(self):
        url = reverse('product-list')
        response = self.client.get(url, {'in_stock': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        for product in response.data['results']:
            self.assertGreater(product['stock_quantity'], 0)

    def test_search_filter(self):
        url = reverse('product-list')
        response = self.client.get(url, {'search': 'laptop'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Laptop')

    def test_ordering_filter(self):
        url = reverse('product-list')
        # Test ascending order
        response = self.client.get(url, {'ordering': 'price'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [p['price'] for p in response.data['results']]
        self.assertEqual(prices, sorted(prices))
        
        # Test descending order
        response = self.client.get(url, {'ordering': '-price'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [p['price'] for p in response.data['results']]
        self.assertEqual(prices, sorted(prices, reverse=True))