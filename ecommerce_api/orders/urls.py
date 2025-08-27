from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

router = DefaultRouter()
router.register(r'', views.OrderViewSet, basename='order')

orders_router = routers.NestedSimpleRouter(router, r'', lookup='order')
orders_router.register(r'payments', views.PaymentViewSet, basename='order-payments')
orders_router.register(r'shipping', views.ShippingViewSet, basename='order-shipping')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(orders_router.urls)),
]
