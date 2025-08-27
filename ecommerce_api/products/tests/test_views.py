from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Product, Category, Brand, Wishlist, ProductReview
from decimal import Decimal

User = get_user_model()

class ProductAPIViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="user@test.com", password="pass123")
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.brand = Brand.objects.create(name="BrandX")
        self.product = Product.objects.create(
            name="Sample Product",
            slug="sample-product",
            description="Sample Description",
            price=Decimal("99.99"),
            sku="SKU1234",
            quantity=10,
            category=self.category,
            brand=self.brand,
            created_by=self.user,
            updated_by=self.user,
            status="ACTIVE",
        )
        self.review = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=4,
            title="Good product",
            comment="I like it",
            is_approved=True,
        )
        self.wishlist = Wishlist.objects.create(user=self.user, product=self.product)


    def test_product_detail_api(self):
        url = reverse('products:product_detail', kwargs={'pk': self.product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.product.id)

    def test_category_list_api(self):
        url = reverse('products:category_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', [])
        self.assertTrue(any(c['id'] == self.category.id for c in results))

    def test_category_detail_api(self):
        url = reverse('products:category_detail', kwargs={'pk': self.category.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.category.id)

    def test_brand_list_api(self):
        url = reverse('products:brand_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', [])
        self.assertTrue(any(b['id'] == self.brand.id for b in results))

    def test_brand_list_api(self):
        url = reverse('products:brand_list')  # Correct API name from your URLs
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # response.data is paginated dict or list, handle both
        data = response.data
        if isinstance(data, dict):
            results = data.get('results', [])
        else:
            results = data

        self.assertTrue(any(b['id'] == self.brand.id for b in results))


    def test_product_review_list_api(self):
        url = reverse('products:review_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', [])
        self.assertTrue(any(r['id'] == self.review.id for r in results))

    def test_wishlist_list_api(self):
        url = reverse('products:wishlist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', [])
        self.assertTrue(any(w['id'] == self.wishlist.id for w in results))

    def test_create_product_api_permission_denied_for_non_admin(self):
        url = reverse('products:product_list')
        data = {
            "name": "New Product",
            "slug": "new-product",
            "description": "Test product",
            "price": "12.99",
            "sku": "SKU9999",
            "quantity": 5,
            "category": self.category.id,
            "brand": self.brand.id,
            "status": "ACTIVE"
        }
        response = self.client.post(url, data, format='json')
        # Non admin is disallowed, expect 403 or 405 depending on your permission setup
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED])

    def test_product_recommendations_api(self):
        url = reverse('products:product_recommendations', kwargs={'product_id': self.product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_search_api_get(self):
        url = reverse('products:product_search')
        response = self.client.get(url, {'q': 'Sample'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        # If paginated, data is dict with 'results'; if plain list, use data directly
        results = data.get('results', data) if isinstance(data, dict) else data
        self.assertTrue(any(p['id'] == self.product.id for p in results))


    def test_product_search_api_post(self):
        url = reverse('products:product_search')
        response = self.client.post(url, {'q': 'Sample'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        if isinstance(data, dict):  # paginated
            results = data.get('results', [])
        else:
            results = data
        self.assertTrue(any(p['id'] == self.product.id for p in results))
