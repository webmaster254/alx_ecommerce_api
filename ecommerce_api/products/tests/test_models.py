from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from products.models import (
    Category, Brand, Product, ProductImage, ProductReview, ProductActivity, Wishlist
)

User = get_user_model()

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics", slug="electronics")

    def test_string_representation(self):
        self.assertEqual(str(self.category), "Electronics")

    def test_get_absolute_url(self):
        url = self.category.get_absolute_url()
        self.assertIn(self.category.slug, url)


class BrandModelTest(TestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name="ACME")

    def test_string_representation(self):
        self.assertEqual(str(self.brand), "ACME")

    def test_get_absolute_url(self):
        url = self.brand.get_absolute_url()
        self.assertIn(str(self.brand.pk), url)


class ProductModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', password='pass1234')
        self.category = Category.objects.create(name="Books", slug="books")
        self.brand = Brand.objects.create(name="Readers Inc.")
        self.product = Product.objects.create(
            name="Sample Book",
            slug="sample-book",
            description="A sample book.",
            price=Decimal('15.00'),
            sku="SKU123",
            quantity=10,
            category=self.category,
            brand=self.brand,
            created_by=self.user,
            updated_by=self.user,
            status='ACTIVE'
        )

    def test_string_representation(self):
        self.assertEqual(str(self.product), "Sample Book")

    def test_get_absolute_url(self):
        url = self.product.get_absolute_url()
        self.assertIn(self.product.slug, url)

    def test_slug_generation_on_save(self):
        # change the name and save to trigger slug update
        self.product.name = "Updated Book"
        self.product.save()
        self.assertTrue(self.product.slug.startswith("updated-book"))

    def test_discount_percentage(self):
        self.product.compare_price = Decimal('20.00')
        self.product.price = Decimal('15.00')
        self.assertEqual(self.product.discount_percentage, 25)

    def test_discount_percentage_no_compare_price(self):
        self.product.compare_price = None
        self.assertEqual(self.product.discount_percentage, 0)

    def test_is_in_stock_and_low_stock(self):
        self.product.quantity = 10
        self.assertTrue(self.product.is_in_stock)
        self.assertFalse(self.product.is_low_stock)

        self.product.quantity = 3
        self.assertTrue(self.product.is_low_stock)

    def test_reduce_stock_success_and_failure(self):
        stock_before = self.product.quantity
        result = self.product.reduce_stock(2)
        self.product.refresh_from_db()
        self.assertTrue(result)
        self.assertEqual(self.product.quantity, stock_before - 2)

        # Try reducing more than quantity available
        result = self.product.reduce_stock(1000)
        self.assertFalse(result)

    def test_average_rating_and_review_count(self):
        # Initially no reviews
        self.assertEqual(self.product.average_rating, 0)
        self.assertEqual(self.product.review_count, 0)

        user2 = User.objects.create_user(email='user2@example.com', password='pass1234')

        # Add approved review
        review1 = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            title="Great!",
            comment="Loved it",
            is_approved=True
        )
        # Add non-approved review
        review2 = ProductReview.objects.create(
            product=self.product,
            user=user2,
            rating=3,
            title="Okay",
            comment="Not bad",
            is_approved=False
        )
        self.assertEqual(self.product.average_rating, 5)
        self.assertEqual(self.product.review_count, 1)


class ProductImageModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Category 1", slug="category-1")
        self.product = Product.objects.create(
            name="Product 1",
            slug="product-1",
            description="Description",
            price=Decimal('10.00'),
            sku="SKU1",
        )
        self.image = ProductImage.objects.create(
            product=self.product,
            is_primary=True
        )

    def test_string_repr(self):
        self.assertIn(self.product.name, str(self.image))

    def test_ordering(self):
        self.assertEqual(ProductImage._meta.ordering, ['order', 'created_at'])


class ProductReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='reviewer@example.com', password='testpass')
        self.product = Product.objects.create(
            name="Reviewed Product", slug="reviewed-product", description="desc", price=Decimal('20.00'), sku="SKU2"
        )
        self.review = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=4,
            title="Nice Product",
            comment="Good value",
            is_approved=True,
        )

    def test_unique_together(self):
        meta = ProductReview._meta
        self.assertIn(('product', 'user'), meta.unique_together)

    def test_string_representation(self):
        self.assertIn(str(self.user.email), str(self.review))
        self.assertIn(self.product.name, str(self.review))


class ProductActivityModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='tester@example.com', password='pass')
        self.product = Product.objects.create(
            name="Active Product", slug="active-product", description="desc", price=Decimal('30.00'), sku="SKU3"
        )
        self.activity = ProductActivity.objects.create(
            product=self.product, user=self.user, action='view', details={"info": "test"}
        )

    def test_string_representation(self):
        self.assertIn(self.activity.action, str(self.activity))
        self.assertIn(self.product.name, str(self.activity))

    def test_index_fields(self):
    # Get all index fields as list of lists
        indexes = [list(index.fields) for index in ProductActivity._meta.indexes]

        self.assertIn(['product', 'action'], indexes)
        self.assertIn(['user', 'action'], indexes)
        self.assertIn(['timestamp'], indexes)



class WishlistModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='wishlistuser@example.com', password='pass')
        self.product = Product.objects.create(
            name="Wish Product", slug="wish-product", description="desc", price=Decimal('15.00'), sku="SKU4"
        )
        self.wishlist = Wishlist.objects.create(user=self.user, product=self.product)

    def test_unique_together(self):
        meta = Wishlist._meta
        self.assertIn(('user', 'product'), meta.unique_together)

    def test_string_representation(self):
        self.assertIn(self.user.email, str(self.wishlist))
        self.assertIn(self.product.name, str(self.wishlist))
