from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cart-items', views.CartItemViewSet, basename='cartitem')
router.register(r'saved-carts', views.SavedCartViewSet, basename='savedcart')
router.register(r'', views.CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
]