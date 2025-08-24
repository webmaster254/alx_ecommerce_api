from django.urls import path
from . import views
from .views import (
    ProductListView, ProductDetailView, ProductCreateView,
    ProductUpdateView, ProductDeleteView, WishlistListView,
    # API Views
    ProductListAPIView, ProductDetailAPIView,
    CategoryListAPIView, CategoryDetailAPIView,
    BrandListAPIView, BrandDetailAPIView,
    ProductReviewListAPIView, WishlistAPIView
)

app_name = 'products'

urlpatterns = [
    # API Root
    path('', views.api_root, name='api_root'),

    # ---------
    # API URLs 
    # ---------
    path('categories/', CategoryListAPIView.as_view(), name='category_list'),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='category_detail'),
    path('brands/', BrandListAPIView.as_view(), name='brand_list'),
    path('brands/<int:pk>/', BrandDetailAPIView.as_view(), name='brand_detail'),
    path('reviews/', ProductReviewListAPIView.as_view(), name='review_list'),
    path('wishlist/', WishlistAPIView.as_view(), name='wishlist'),
    path('<int:product_id>/recommendations/', views.product_recommendations_api, name='product_recommendations'),
    path('search/', views.product_search_api, name='product_search'),
    path('<int:pk>/', ProductDetailAPIView.as_view(), name='product_detail'),
    path('', ProductListAPIView.as_view(), name='product_list'),

    # -----------------------
    # HTML Template URLs
    # -----------------------
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('brand/<int:pk>/', views.brand_detail, name='brand_detail'),
    path('create/', ProductCreateView.as_view(), name='product_create'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('<slug:slug>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('<slug:slug>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('<slug:slug>/review/', views.add_review, name='add_review'),
    path('<slug:slug>/wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/', WishlistListView.as_view(), name='wishlist'),
    path('search/', views.search_products, name='search'),
]
