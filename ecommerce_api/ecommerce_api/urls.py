# ecommerce_api/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls import handler404, handler500, handler403, handler400
from django.views.generic import TemplateView  # Add this import
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),  
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/cart/', include('cart.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/promotions/', include('promotions.urls')),
    path('', views.home_view, name='home'),
    
    

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='api-docs'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Custom error handlers
handler404 = 'ecommerce_api.views.custom_404'  # Use string reference
handler500 = 'ecommerce_api.views.custom_500'
handler403 = 'ecommerce_api.views.custom_403'
handler400 = 'ecommerce_api.views.custom_400'

# Only serve media files in development
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)