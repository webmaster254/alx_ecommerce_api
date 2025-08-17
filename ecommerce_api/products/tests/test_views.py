from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from products.models import Product, Category
from users.models import CustomUser

class ProductViewSetTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic items'
        )
        self.product = Product.objects.create(
            name='Laptop',
            description='High performance laptop',
            price=999.99,
            category=self.category,
            stock_quantity=10,
            created_by=self.user
        )

    def test_list_products(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_product(self):
        url = reverse('product-detail', args=[self.product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Laptop')

    def test_create_product_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product-list')
        data = {
            'name': 'Smartphone',
            'description': 'Latest smartphone',
            'price': 799.99,
            'category_id': self.category.id,
            'stock_quantity': 15
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_create_product_unauthenticated(self):
        url = reverse('product-list')
        data = {
            'name': 'Smartphone',
            'description': 'Latest smartphone',
            'price': 799.99,
            'category_id': self.category.id,
            'stock_quantity': 15
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_product_owner(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product-detail', args=[self.product.id])
        data = {'price': 899.99}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, 899.99)

    def test_update_product_non_owner(self):
        other_user = CustomUser.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        self.client.force_authenticate(user=other_user)
        url = reverse('product-detail', args=[self.product.id])
        data = {'price': 899.99}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_product_owner(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product-detail', args=[self.product.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

    def test_reduce_stock(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product-reduce-stock', args=[self.product.id])
        data = {'quantity': 3}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 7)

        # Test insufficient stock
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)