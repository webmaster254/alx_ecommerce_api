from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'suppliers', views.SupplierViewSet)
router.register(r'inventory', views.InventoryViewSet)
router.register(r'stock-movements', views.StockMovementViewSet, basename='stockmovement')
router.register(r'purchase-orders', views.PurchaseOrderViewSet)
router.register(r'stock-adjustments', views.StockAdjustmentViewSet, basename='stockadjustment')

urlpatterns = [
    path('', include(router.urls)),
]