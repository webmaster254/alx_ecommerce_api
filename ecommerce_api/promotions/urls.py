# promotions/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'promotion-types', views.PromotionTypeViewSet)
router.register(r'coupons', views.CouponViewSet, basename='coupon')
router.register(r'promotions', views.PromotionViewSet, basename='promotion')
router.register(r'bundle-offers', views.BundleOfferViewSet, basename='bundleoffer')
router.register(r'promotion-usages', views.PromotionUsageViewSet, basename='promotionusage')
router.register(r'coupon-usages', views.CouponUsageViewSet, basename='couponusage')
router.register(r'promo-banners', views.PromoBannerViewSet, basename='promobanner')
router.register(r'public/promotions', views.PublicPromotionsViewSet, basename='public-promotions')

urlpatterns = [
    path('', include(router.urls)),
]