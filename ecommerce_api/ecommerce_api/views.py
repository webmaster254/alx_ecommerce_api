# ecommerce_api/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from django.contrib.auth import get_user_model
from products.models import Product, Category, ProductReview

User = get_user_model()

def home_view(request):
    """Home page view with stats"""
    context = {
        'product_count': Product.objects.filter(status='ACTIVE').count(),
        'user_count': User.objects.count(),
        'review_count': ProductReview.objects.filter(is_approved=True).count(),
        'category_count': Category.objects.count(),
    }
    return render(request, 'home.html', context)

def custom_404(request, exception):
    """Custom 404 error handler"""
    return render(request, '404.html', status=404)

def custom_500(request):
    """Custom 500 error handler"""
    return render(request, '500.html', status=500)

def custom_403(request, exception):
    """Custom 403 error handler"""
    return render(request, '403.html', status=403)

def custom_400(request, exception):
    """Custom 400 error handler"""
    return render(request, '400.html', status=400)