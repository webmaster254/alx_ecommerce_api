from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Supplier, Inventory, StockMovement, PurchaseOrder, PurchaseOrderItem, StockAdjustment
from .serializers import (
    SupplierSerializer, InventorySerializer, StockMovementSerializer,
    PurchaseOrderSerializer, PurchaseOrderItemSerializer, StockAdjustmentSerializer
)
from .permissions import IsInventoryManager, IsOwnerOrInventoryManager
from .utils import InventoryUtils, StockValidator, InventoryReports

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsInventoryManager]

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.select_related('product').all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'adjust_stock']:
            return [IsAuthenticated(), IsInventoryManager()]
        return super().get_permissions()

    @action(detail=True, methods=['post'], permission_classes=[IsInventoryManager])
    def adjust_stock(self, request, pk=None):
        inventory = self.get_object()
        quantity = request.data.get('quantity')
        reason = request.data.get('reason', '')
        adjustment_type = request.data.get('adjustment_type', 'correction')

        try:
            StockValidator.validate_positive_quantity(int(quantity))
            
            InventoryUtils.adjust_stock(
                inventory=inventory,
                adjustment_type=adjustment_type,
                quantity=int(quantity),
                reason=reason,
                user=request.user
            )
            
            return Response({'message': 'Stock adjusted successfully'})
            
        except (ValueError, ValidationError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockMovement.objects.select_related('inventory__product', 'created_by').all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated, IsInventoryManager]

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.select_related('supplier', 'created_by').prefetch_related('items__product').all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, IsInventoryManager]

    def perform_create(self, serializer):
        order_number = InventoryUtils.generate_order_number()
        serializer.save(order_number=order_number, created_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsInventoryManager])
    def receive_stock(self, request, pk=None):
        purchase_order = self.get_object()
        
        if purchase_order.status != 'ordered':
            return Response({'error': 'Only ordered purchase orders can be received'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                for item in purchase_order.items.all():
                    # Get or create inventory
                    inventory, created = Inventory.objects.get_or_create(
                        product=item.product,
                        defaults={'stock_level': 0, 'low_stock_threshold': 10}
                    )
                    
                    # Update stock
                    InventoryUtils.update_stock_level(
                        inventory=inventory,
                        quantity=item.quantity,
                        movement_type='in',
                        reference=purchase_order.order_number,
                        notes=f"Received from purchase order {purchase_order.order_number}",
                        user=request.user
                    )
                    
                    # Update received quantity
                    item.received_quantity = item.quantity
                    item.save()

                # Update purchase order status
                purchase_order.status = 'received'
                purchase_order.save()

            return Response({'message': 'Stock received successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsInventoryManager])
    def low_stock_report(self, request):
        """
        Get report of low stock items
        """
        threshold = request.GET.get('threshold')
        low_stock_items = InventoryUtils.get_low_stock_items(
            threshold=int(threshold) if threshold else None
        )
        
        data = [{
            'product': item['inventory'].product.name,
            'available_stock': item['available_stock'],
            'threshold': item['threshold'],
            'is_critical': item['available_stock'] == 0
        } for item in low_stock_items]
        
        return Response(data)

    @action(detail=False, methods=['get'], permission_classes=[IsInventoryManager])
    def inventory_summary(self, request):
        """
        Get inventory summary report
        """
        summary = InventoryReports.get_inventory_summary()
        return Response(summary)

class StockAdjustmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockAdjustment.objects.select_related('inventory__product', 'adjusted_by').all()
    serializer_class = StockAdjustmentSerializer
    permission_classes = [IsAuthenticated, IsInventoryManager]