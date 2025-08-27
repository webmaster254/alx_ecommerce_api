from django.test import TestCase
from decimal import Decimal
from django.utils import timezone
from inventory.models import Supplier, Inventory, StockMovement, PurchaseOrder, PurchaseOrderItem, StockAdjustment
from products.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

class InventoryModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='tester@example.com', password='pass')
        self.product = Product.objects.create(
            name='Sample Product', slug='sample-product',
            price=Decimal('100.00'), sku='SP001', quantity=100, status='ACTIVE'
        )
        self.supplier = Supplier.objects.create(
            name='Supplier Inc.', contact_person='John Doe',
            email='contact@supplier.com', phone='1234567890',
            address='123 Supplier St'
        )
        self.inventory = Inventory.objects.create(
            product=self.product,
            stock_level=100,
            low_stock_threshold=10,
            reserved_stock=5
        )

    def test_supplier_str(self):
        self.assertEqual(str(self.supplier), 'Supplier Inc.')

    def test_inventory_available_stock(self):
        self.assertEqual(self.inventory.available_stock(), 95)

    def test_inventory_is_low_stock(self):
        self.assertFalse(self.inventory.is_low_stock())
        self.inventory.reserved_stock = 95
        self.inventory.save()
        self.assertTrue(self.inventory.is_low_stock())

    def test_inventory_str(self):
        self.assertEqual(str(self.inventory), f"{self.product.name} - Stock: {self.inventory.stock_level}")

    def test_stock_movement_creation(self):
        movement = StockMovement.objects.create(
            inventory=self.inventory,
            movement_type='in',
            quantity=10,
            reference='ORDER123',
            notes='Stock added for order 123',
            created_by=self.user
        )
        self.assertEqual(movement.movement_type, 'in')
        self.assertEqual(movement.quantity, 10)
        self.assertEqual(movement.reference, 'ORDER123')

    def test_purchase_order_creation(self):
        po = PurchaseOrder.objects.create(
            supplier=self.supplier,
            order_number='PO12345',
            status='draft',
            expected_delivery=timezone.now().date(),
            notes='Urgent order',
            created_by=self.user
        )
        self.assertEqual(po.status, 'draft')
        self.assertEqual(po.order_number, 'PO12345')

    def test_purchase_order_item_creation(self):
        po = PurchaseOrder.objects.create(
            supplier=self.supplier,
            order_number='PO54321',
            created_by=self.user
        )
        po_item = PurchaseOrderItem.objects.create(
            purchase_order=po,
            product=self.product,
            quantity=50,
            received_quantity=0,
            unit_cost=Decimal('20.00')
        )
        self.assertEqual(po_item.quantity, 50)
        self.assertEqual(po_item.unit_cost, Decimal('20.00'))
    
    def test_stock_adjustment_creation(self):
        adjustment = StockAdjustment.objects.create(
            inventory=self.inventory,
            adjustment_type='add',
            quantity=20,
            reason='Stock correction',
            adjusted_by=self.user
        )
        self.assertEqual(adjustment.adjustment_type, 'add')
        self.assertEqual(adjustment.quantity, 20)
        self.assertEqual(adjustment.reason, 'Stock correction')
