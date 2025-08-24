from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.OrderViewSet, basename='order')
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'shipping', views.ShippingViewSet, basename='shipping')

urlpatterns = [
    path('', include(router.urls)),
]