from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.db.models import Q
from .models import (
    PromotionType, Coupon, Promotion, BundleOffer, 
    PromotionUsage, CouponUsage, PromoBanner
)
from .serializers import (
    PromotionTypeSerializer, CouponSerializer, PromotionSerializer,
    BundleOfferSerializer, PromotionUsageSerializer, CouponUsageSerializer,
    PromoBannerSerializer, ApplyCouponSerializer, CouponValidationResponseSerializer,
    ActivePromotionsSerializer
)
from .permissions import IsPromotionManager, CanUsePromotion
from .utils import PromotionUtils

class PromotionTypeViewSet(viewsets.ModelViewSet):
    queryset = PromotionType.objects.all()
    serializer_class = PromotionTypeSerializer
    permission_classes = [IsAuthenticated, IsPromotionManager]

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.prefetch_related('applicable_categories', 'applicable_products').all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated, IsPromotionManager]

    @action(detail=False, methods=['post'], permission_classes=[CanUsePromotion])
    def validate(self, request):
        serializer = ApplyCouponSerializer(data=request.data)
        if serializer.is_valid():
            coupon_code = serializer.validated_data['coupon_code']
            order_amount = serializer.validated_data['order_amount']
            user = request.user if request.user.is_authenticated else None
            
            result = PromotionUtils.validate_coupon(coupon_code, user, order_amount)
            
            response_serializer = CouponValidationResponseSerializer({
                'is_valid': result['is_valid'],
                'discount_amount': result['discount_amount'],
                'message': result['message'],
                'coupon': result.get('coupon')
            })
            
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.prefetch_related('categories', 'products').all()
    serializer_class = PromotionSerializer
    permission_classes = [IsAuthenticated, IsPromotionManager]

    @action(detail=False, methods=['get'], permission_classes=[])
    def active(self, request):
        active_promotions = PromotionUtils.get_active_promotions()
        serializer = self.get_serializer(active_promotions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[])
    def applicable_products(self, request, pk=None):
        promotion = self.get_object()
        products = promotion.products.all()
        # You might want to add more logic here based on categories
        from products.serializers import ProductSerializer
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class BundleOfferViewSet(viewsets.ModelViewSet):
    queryset = BundleOffer.objects.select_related('promotion').all()
    serializer_class = BundleOfferSerializer
    permission_classes = [IsAuthenticated, IsPromotionManager]

class PromotionUsageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PromotionUsage.objects.select_related('promotion', 'user').all()
    serializer_class = PromotionUsageSerializer
    permission_classes = [IsAuthenticated, IsPromotionManager]

class CouponUsageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CouponUsage.objects.select_related('coupon', 'user').all()
    serializer_class = CouponUsageSerializer
    permission_classes = [IsAuthenticated, IsPromotionManager]

class PromoBannerViewSet(viewsets.ModelViewSet):
    queryset = PromoBanner.objects.all()
    serializer_class = PromoBannerSerializer
    permission_classes = [IsAuthenticated, IsPromotionManager]

    @action(detail=False, methods=['get'], permission_classes=[])
    def active(self, request):
        now = timezone.now()
        active_banners = PromoBanner.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('display_order')
        serializer = self.get_serializer(active_banners, many=True)
        return Response(serializer.data)

class PublicPromotionsViewSet(viewsets.ViewSet):
    """Public endpoints for promotions"""
    permission_classes = []

    @action(detail=False, methods=['get'])
    def all_active(self, request):
        active_promotions = PromotionUtils.get_active_promotions()
        active_banners = PromoBanner.objects.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).order_by('display_order')
        
        serializer = ActivePromotionsSerializer({
            'promotions': active_promotions,
            'banners': active_banners
        })
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def for_product(self, request):
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({'error': 'product_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from products.models import Product
            product = Product.objects.get(id=product_id)
            promotions = PromotionUtils.get_product_promotions(product)
            serializer = PromotionSerializer(promotions, many=True)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)