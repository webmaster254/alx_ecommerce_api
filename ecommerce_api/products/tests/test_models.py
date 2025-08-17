from django.test import TestCase
from django.core.exceptions import ValidationError
from products.models import Product, Category
from users.models import CustomUser

class ProductModelTest(TestCase):
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
        product = Product.objects.create(
            name='Laptop',
            description='High performance laptop',
            price=999.99,
            category=self.category,
            stock_quantity=10,
            created_by=self.user
        )
        self.assertEqual(product.name, 'Laptop')
        self.assertEqual(product.price, 999.99)
        self.assertEqual(product.category.name, 'Electronics')
        self.assertEqual(product.created_by.username, 'testuser')

    def test_price_validation(self):
        with self.assertRaises(ValidationError):
            product = Product(
                name='Invalid Product',
                description='Test',
                price=-10.00,
                category=self.category,
                stock_quantity=5,
                created_by=self.user
            )
            product.full_clean()

    def test_stock_quantity_validation(self):
        with self.assertRaises(ValidationError):
            product = Product(
                name='Invalid Product',
                description='Test',
                price=10.00,
                category=self.category,
                stock_quantity=-5,
                created_by=self.user
            )
            product.full_clean()

    def test_reduce_stock(self):
        product = Product.objects.create(
            name='Phone',
            description='Smartphone',
            price=699.99,
            category=self.category,
            stock_quantity=5,
            created_by=self.user
        )
        self.assertTrue(product.reduce_stock(3))
        product.refresh_from_db()
        self.assertEqual(product.stock_quantity, 2)
        self.assertFalse(product.reduce_stock(3))
        product.refresh_from_db()
        self.assertEqual(product.stock_quantity, 2)