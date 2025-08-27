from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import serializers
from products.models import Product, Category, Brand, ProductReview, Wishlist, ProductImage
from products.serializers import (
    CategorySerializer, BrandSerializer, ProductImageSerializer,
    ProductReviewSerializer, ProductSerializer, WishlistSerializer,
    ProductSearchSerializer
)
from decimal import Decimal
from rest_framework.exceptions import ValidationError

User = get_user_model()

class CategorySerializerTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics", slug="electronics")

    def test_category_serialization(self):
        serializer = CategorySerializer(instance=self.category)
        data = serializer.data
        self.assertEqual(data['name'], self.category.name)
        self.assertEqual(data['slug'], self.category.slug)


class BrandSerializerTest(TestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name="BrandX", description="A brand.")

    def test_brand_serialization(self):
        serializer = BrandSerializer(instance=self.brand)
        data = serializer.data
        self.assertEqual(data['name'], self.brand.name)
        self.assertEqual(data['description'], self.brand.description)


class ProductImageSerializerTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Prod", slug="prod", description="desc",
                             price=Decimal('10.00'), sku="SKU001", quantity=5)
        self.image = ProductImage.objects.create(product=self.product, is_primary=True, alt_text="Alt text")

    def test_image_serialization(self):
        serializer = ProductImageSerializer(instance=self.image)
        data = serializer.data
        self.assertEqual(data['alt_text'], self.image.alt_text)
        self.assertEqual(data['is_primary'], self.image.is_primary)


class ProductReviewSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', password='testpass')
        self.product = Product.objects.create(name="Prod", slug="prod", description="desc",
                             price=Decimal('10.00'), sku="SKU001", quantity=5)
        self.review = ProductReview.objects.create(product=self.product, user=self.user,
                                                   rating=4, title="Good", comment="Nice", is_approved=True)

    def test_review_serialization(self):
        serializer = ProductReviewSerializer(instance=self.review, context={'request': None})
        data = serializer.data
        self.assertEqual(data['rating'], self.review.rating)
        self.assertEqual(data['title'], self.review.title)
        self.assertEqual(data['user_email'], self.user.email)
        self.assertEqual(data['product_name'], self.product.name)
        # user_name returns first + last or email
        self.assertTrue('user_name' in data)

    def test_rating_validation(self):
        serializer = ProductReviewSerializer(data={'rating': 6, 'product': self.product.id},
                                             context={'request': type('Request', (), {'user': self.user})()})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_create_review_duplicate(self):
        context = {'request': type('Req', (), {'user': self.user})()}
        data = {
            'product': self.product.id,
            'rating': 4,
            'title': 'Duplicate review',
            'comment': 'Testing duplicate'
        }
        serializer = ProductReviewSerializer(data=data, context=context)
        self.assertTrue(serializer.is_valid())  # Validation passes
        with self.assertRaises(serializers.ValidationError) as exc:
            serializer.save()
        self.assertIn('You have already reviewed this product.', str(exc.exception))


class ProductSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', password='testpass')
        self.category = Category.objects.create(name="Category", slug="category")
        self.brand = Brand.objects.create(name="Brand")
        self.product = Product.objects.create(
            name="Prod", slug="prod", description="desc", price=Decimal('20.00'),
            compare_price=Decimal('30.00'), cost=Decimal('10.00'), sku="SKU001", quantity=10,
            category=self.category, brand=self.brand, created_by=self.user, updated_by=self.user,
            status='ACTIVE'
        )

    def test_product_serialization(self):
        serializer = ProductSerializer(instance=self.product)
        data = serializer.data
        self.assertEqual(data['name'], self.product.name)
        self.assertEqual(data['discount_percentage'], 33)  # ((30-20)/30 *100) = 33%
        self.assertEqual(data['category_name'], self.category.name)
        self.assertEqual(data['brand_name'], self.brand.name)
        self.assertEqual(data['created_by_email'], self.user.email)

    def test_price_validation(self):
        serializer = ProductSerializer(data={'price': -1, 'quantity': 1, 'name':'X', 'sku': 'sku1', 'category': self.category.id, 'status': 'ACTIVE'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('price', serializer.errors)

    def test_quantity_validation(self):
        serializer = ProductSerializer(data={'price': 10, 'quantity': -1, 'name':'X', 'sku': 'sku1', 'category': self.category.id, 'status': 'ACTIVE'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('quantity', serializer.errors)

    def test_compare_price_validation(self):
        data = {
            'name': 'Test Product',
            'description': 'A test product',
            'price': Decimal('10.00'),
            'compare_price': Decimal('5.00'),  # Invalid: less than price
            'quantity': 1,
            'sku': 'SKU123',
            'category': self.category.id,
            'status': 'ACTIVE'
        }
        serializer = ProductSerializer(data=data)
        valid = serializer.is_valid()
        self.assertFalse(valid)
        self.assertIn('compare_price', serializer.errors)


class WishlistSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', password='testpass')
        self.category = Category.objects.create(name="Category", slug="category")
        self.product = Product.objects.create(name="Prod", slug="prod", price=Decimal('10.00'), sku="SKU001", quantity=10, category=self.category)
        self.wishlist = Wishlist.objects.create(user=self.user, product=self.product)

    def test_wishlist_serialization(self):
        serializer = WishlistSerializer(instance=self.wishlist)
        data = serializer.data
        self.assertEqual(data['product_name'], self.product.name)
        self.assertEqual(float(data['product_price']), float(self.product.price))
        self.assertEqual(data['product_slug'], self.product.slug)

    def test_wishlist_create_duplicate(self):
        context = {'request': type('Req', (), {'user': self.user})()}
        data = {'product': self.product.id}
        serializer = WishlistSerializer(data=data, context=context)
        self.assertTrue(serializer.is_valid())  # Validation passes
        with self.assertRaises(serializers.ValidationError) as exc:
            serializer.save()
        self.assertIn('Product is already in your wishlist.', str(exc.exception))



class ProductSearchSerializerTest(TestCase):
    def test_min_price_validation(self):
        serializer = ProductSearchSerializer(data={'min_price': -1})
        self.assertFalse(serializer.is_valid())
        self.assertIn('min_price', serializer.errors)

    def test_max_price_validation(self):
        serializer = ProductSearchSerializer(data={'max_price': -1})
        self.assertFalse(serializer.is_valid())
        self.assertIn('max_price', serializer.errors)
