# products/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.generic import TemplateView
from django.db.models import Count

# Django REST Framework imports
from rest_framework import generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse

# Local imports
from .models import Product, ProductReview, Category, Brand, Wishlist
from .forms import ProductForm, ProductReviewForm
from .serializers import (
    ProductSerializer, CategorySerializer, BrandSerializer,
    ProductReviewSerializer, WishlistSerializer, ProductSearchSerializer
)
from .utils import get_product_recommendations


CustomUser = get_user_model()

# ============================================================================
# HTML TEMPLATE VIEWS (For regular web pages)
# ============================================================================

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(status='ACTIVE')
        
        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()
        
        # Category filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
            
        # Brand filter
        brand_id = self.request.GET.get('brand')
        if brand_id:
            queryset = queryset.filter(brand__id=brand_id)
            
        # Tag filter
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__name__in=[tag])
            
        # Price range filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        # Ordering
        ordering = self.request.GET.get('ordering', '-created_at')
        if ordering in ['name', 'price', '-price', 'created_at', '-created_at']:
            queryset = queryset.order_by(ordering)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        context['search_query'] = self.request.GET.get('q', '')
        return context
    

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add stats to context
        context['product_count'] = Product.objects.filter(status='ACTIVE').count()
        context['user_count'] = CustomUser.objects.count()
        context['review_count'] = ProductReview.objects.filter(is_approved=True).count()
        context['category_count'] = Category.objects.count()
        
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_form'] = ProductReviewForm()
        context['reviews'] = self.object.reviews.filter(is_approved=True)
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    
    def test_func(self):
        product = self.get_object()
        return self.request.user.is_staff or product.created_by == self.request.user


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')
    
    def test_func(self):
        product = self.get_object()
        return self.request.user.is_staff or product.created_by == self.request.user


class WishlistListView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = 'products/wishlist.html'
    context_object_name = 'wishlist_items'
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)


# ============================================================================
# FUNCTION-BASED HTML VIEWS
# ============================================================================

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, status='ACTIVE')
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': page_obj,
    }
    return render(request, 'products/category_detail.html', context)


def brand_detail(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    products = Product.objects.filter(brand=brand, status='ACTIVE')
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'brand': brand,
        'products': page_obj,
    }
    return render(request, 'products/brand_detail.html', context)


@login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            
            # Check if user already reviewed this product
            existing_review = ProductReview.objects.filter(product=product, user=request.user).first()
            if existing_review:
                messages.error(request, 'You have already reviewed this product.')
                return redirect('products:product_detail', slug=slug)
                
            review.save()
            messages.success(request, 'Your review has been submitted and is awaiting approval.')
            return redirect('products:product_detail', slug=slug)
    
    return redirect('products:product_detail', slug=slug)


@login_required
def toggle_wishlist(request, slug):
    product = get_object_or_404(Product, slug=slug)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        wishlist_item.delete()
        messages.info(request, 'Product removed from your wishlist.')
    else:
        messages.success(request, 'Product added to your wishlist.')
    
    return redirect('products:product_detail', slug=slug)


def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(status='ACTIVE')
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'search_query': query,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
    }
    
    return render(request, 'products/search_results.html', context)


# ============================================================================
# API VIEWS (Django REST Framework)
# ============================================================================

class ProductListAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.filter(status='ACTIVE').order_by('-created_at')  
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'is_featured']
    search_fields = ['name', 'description', 'tags__name']
    ordering_fields = ['name', 'price', 'created_at', 'average_rating']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CategoryDetailAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class BrandListAPIView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]


class BrandDetailAPIView(generics.RetrieveAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]


class ProductReviewListAPIView(generics.ListCreateAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return ProductReview.objects.filter(is_approved=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WishlistAPIView(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ============================================================================
# API FUNCTION-BASED VIEWS
# ============================================================================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def product_recommendations_api(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        recommendations = get_product_recommendations(product)
        serializer = ProductSerializer(recommendations, many=True, context={'request': request})
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def product_search_api(request):
    if request.method == 'GET':
        # Handle GET requests with query parameters
        query = request.GET.get('q', '')
        category = request.GET.get('category', '')
        brand = request.GET.get('brand', '')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        
        queryset = Product.objects.filter(status='ACTIVE')
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()
        
        if category:
            queryset = queryset.filter(category__slug=category)
            
        if brand:
            queryset = queryset.filter(brand__id=brand)
            
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
            
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        serializer = ProductSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Handle POST requests with JSON body
        serializer = ProductSearchSerializer(data=request.data)
        if serializer.is_valid():
            queryset = Product.objects.filter(status='ACTIVE')
            
            if serializer.validated_data.get('q'):
                queryset = queryset.filter(
                    Q(name__icontains=serializer.validated_data['q']) |
                    Q(description__icontains=serializer.validated_data['q']) |
                    Q(tags__name__icontains=serializer.validated_data['q'])
                ).distinct()
            
            results_serializer = ProductSerializer(
                queryset, many=True, context={'request': request}
            )
            return Response(results_serializer.data)
        
        return Response(serializer.errors, status=400)
    
@api_view(['GET'])
def api_root(request, format=None):
    """API root endpoint that lists available endpoints"""
    return Response({
        'products': reverse('products:product_list', request=request, format=format),
        'categories': reverse('products:category_list', request=request, format=format),
        'brands': reverse('products:brand_list', request=request, format=format),
        'reviews': reverse('products:review_list', request=request, format=format),
        'wishlist': reverse('products:wishlist', request=request, format=format),
        'search': reverse('products:product_search', request=request, format=format),
        'recommendations': 'Use /api/products/{id}/recommendations/',
        'documentation': '/api/docs/',
        'schema': '/api/schema/',
    })
