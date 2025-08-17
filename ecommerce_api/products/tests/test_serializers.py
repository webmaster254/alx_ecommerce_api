from django.test import TestCase
from rest_framework.exceptions import ValidationError
from products.serializers import ProductSerializer, CategorySerializer
from products.models import Category
from users.models import CustomUser

class ProductSerializerTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic items'
        )

    def test_create_product(self):
        data = {
            'name': 'Smartphone',
            'description': 'Latest smartphone',
            'price': 799.99,
            'category_id': self.category.id,
            'stock_quantity': 15
        }
        serializer = ProductSerializer(data=data, context={'request': None})
        self.assertTrue(serializer.is_valid())
        product = serializer.save(created_by=self.user)
        self.assertEqual(product.name, 'Smartphone')
        self.assertEqual(product.price, 799.99)
        self.assertEqual(product.category.id, self.category.id)

    def test_invalid_price(self):
        data = {
            'name': 'Invalid Product',
            'description': 'Test',
            'price': -10.00,
            'category_id': self.category.id,
            'stock_quantity': 5
        }
        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('price', serializer.errors)

    def test_missing_required_fields(self):
        data = {
            'description': 'Test',
            'price': 10.00,
            'category_id': self.category.id,
            'stock_quantity': 5
        }
        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

class CategorySerializerTest(TestCase):
    def test_create_category(self):
        data = {
            'name': 'Clothing',
            'description': 'Apparel items'
        }
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        category = serializer.save()
        self.assertEqual(category.name, 'Clothing')
        self.assertEqual(category.description, 'Apparel items')

    def test_name_uniqueness(self):
        Category.objects.create(name='Books', description='Reading materials')
        data = {
            'name': 'Books',
            'description': 'Duplicate category'
        }
        serializer = CategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)