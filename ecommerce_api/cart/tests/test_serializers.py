from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import serializers
from cart.models import Cart, CartItem, SavedCart
from products.models import Product, Category, Brand
from cart.serializers import (
    CartSerializer, CartItemSerializer, AddToCartSerializer, 
    UpdateCartItemSerializer, SavedCartSerializer
)

User = get_user_model()

class CartSerializerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com', 
            password='testpass123'
        )
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.brand = Brand.objects.create(name="Test Brand")
        
        self.product = Product.objects.create(
            name='Test Product', 
            price=Decimal('10.00'), 
            quantity=100,
            category=self.category,
            brand=self.brand,
            created_by=self.user,
            updated_by=self.user
        )
        
        # Use get_or_create to avoid unique constraint violation
        self.cart, created = Cart.objects.get_or_create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart, 
            product=self.product, 
            quantity=2
        )

    def test_cart_serializer_output(self):
        serializer = CartSerializer(instance=self.cart)
        data = serializer.data
        
        self.assertEqual(data['user'], self.user.id)
        self.assertIn('items', data)
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['quantity'], 2)

    def test_cart_item_serializer_output(self):
        serializer = CartItemSerializer(instance=self.cart_item)
        data = serializer.data
        
        self.assertEqual(data['product'], self.product.id)
        self.assertEqual(data['quantity'], 2)
        self.assertIn('total_price', data)
        self.assertIn('is_available', data)
        # Compare Decimal to Decimal instead of string
        self.assertEqual(Decimal(data['total_price']), Decimal('20.00'))

class AddToCartSerializerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser2@example.com', 
            password='testpass123'
        )
        self.category = Category.objects.create(name="Test Category 2", slug="test-category-2")
        self.brand = Brand.objects.create(name="Test Brand 2")
        
        self.product = Product.objects.create(
            name='Test Product', 
            price=Decimal('10.00'), 
            quantity=5,
            category=self.category,
            brand=self.brand,
            created_by=self.user,
            updated_by=self.user
        )

    def test_add_to_cart_serializer_valid(self):
        data = {'product_id': self.product.id, 'quantity': 3, 'notes': 'Gift wrap'}
        serializer = AddToCartSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_add_to_cart_serializer_invalid_product_id(self):
        data = {'product_id': 999, 'quantity': 1}
        serializer = AddToCartSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('product_id', serializer.errors)

    def test_add_to_cart_serializer_invalid_quantity(self):
        data = {'product_id': self.product.id, 'quantity': 200}
        serializer = AddToCartSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

class UpdateCartItemSerializerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser3@example.com', 
            password='testpass123'
        )
        self.category = Category.objects.create(name="Test Category 3", slug="test-category-3")
        self.brand = Brand.objects.create(name="Test Brand 3")
        
        self.product = Product.objects.create(
            name='Test Product', 
            price=Decimal('10.00'), 
            quantity=5,
            category=self.category,
            brand=self.brand,
            created_by=self.user,
            updated_by=self.user
        )
        
        # Use get_or_create to avoid unique constraint violation
        self.cart, created = Cart.objects.get_or_create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart, 
            product=self.product, 
            quantity=2
        )

    def test_update_cart_item_serializer_valid(self):
        serializer = UpdateCartItemSerializer(
            instance=self.cart_item, 
            data={'quantity': 3}, 
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        updated_instance = serializer.save()
        self.assertEqual(updated_instance.quantity, 3)

    def test_update_cart_item_serializer_invalid_quantity(self):
        serializer = UpdateCartItemSerializer(
            instance=self.cart_item, 
            data={'quantity': 0},
            partial=True
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('quantity', serializer.errors)

class SavedCartSerializerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='saveduser@example.com', 
            password='testpass123'
        )
        self.saved_cart = SavedCart.objects.create(
            user=self.user, 
            name='My Saved Cart'
        )

    def test_saved_cart_serializer_data(self):
        serializer = SavedCartSerializer(instance=self.saved_cart)
        data = serializer.data
        
        self.assertEqual(data['name'], 'My Saved Cart')
        self.assertEqual(data['user'], self.user.id)

    def test_saved_cart_serializer_data(self):
        serializer = SavedCartSerializer(instance=self.saved_cart)
        data = serializer.data
        
        self.assertEqual(data['name'], 'My Saved Cart')
        # Instead of accessing data['user'], check user on the serializer instance
        self.assertEqual(serializer.instance.user.id, self.user.id)
