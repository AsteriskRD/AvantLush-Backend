from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import waitlist_signup, preview_email, register, login, ProductViewSet, ArticleViewSet, CartViewSet, CartItemViewSet, OrderViewSet
from django.urls import path
from django.urls import path
from .views import verify_email, resend_verification_email
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, AddressViewSet
from .views import ProductSearchView, ProductRecommendationView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet
from .views import (
    waitlist_signup, 
    preview_email, 
    register, 
    login, 
    ProductViewSet, 
    ArticleViewSet, 
    CartViewSet, 
    CartItemViewSet, 
    OrderViewSet,
    GoogleLoginView,
#    AppleLoginView,
#    apple_login_view,
#    apple_auth_callback,
#    google_login_view,  # Login view for Google OAuth2
    forgot_password,
    reset_password,
    google_auth_callback,
    ProductViewSet, ArticleViewSet, CartViewSet, CartItemViewSet, OrderViewSet,
    WishlistViewSet, WishlistItemViewSet,
    CheckoutViewSet,
    ShippingMethodViewSet,
    SupportTicketViewSet
    
)
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'cart/items', CartItemViewSet, basename='cartitem')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')
router.register(r'wishlist-items', WishlistItemViewSet, basename='wishlist-item')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'shipping-methods', ShippingMethodViewSet, basename='shipping-method')
router.register(r'checkout', CheckoutViewSet, basename='checkout')
router.register(r'support-tickets', SupportTicketViewSet, basename='support-ticket')



# URL patterns for Django Rest Framework API
urlpatterns = [
    path('waitlist/signup/', waitlist_signup, name='waitlist_signup'),
    path('preview_email/', preview_email, name='preview_email'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path('auth/google/callback/', google_auth_callback, name='google_callback'),
#   path('auth/apple/', AppleLoginView.as_view(), name='apple_login'),
#   path('auth/apple/callback/', apple_auth_callback, name='apple_callback'),
    path('verify-email/<str:token>/<str:uidb64>/', verify_email, name='verify_email'),
    path('resend-verification/', resend_verification_email, name='resend_verification'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/<str:uidb64>/<str:token>/', reset_password, name='reset_password'),
    path('products/search/', ProductSearchView.as_view(), name='product-search'),
    path('products/<int:product_id>/recommendations/', ProductRecommendationView.as_view(), name='product-recommendations'),
    path('cart/summary/', CartViewSet.as_view({'get': 'summary'})),
    path('cart/add-item/', CartViewSet.as_view({'post': 'add_item'})),
    path('cart/update-quantity/', CartViewSet.as_view({'post': 'update_quantity'})),
    path('cart/remove-item/', CartViewSet.as_view({'post': 'remove_item'})),
    path('cart/apply-discount/', CartViewSet.as_view({'post': 'apply_discount'})),
    path('cart/clear/', CartViewSet.as_view({'post': 'clear'})),
    path('api/', include('checkout.urls')),
    path('orders/<int:pk>/tracking/', OrderViewSet.as_view({'get': 'tracking_history'})),
    path('orders/<int:pk>/tracking/add/', OrderViewSet.as_view({'post': 'add_tracking_event'})),
    path('orders/filter-by-date/', OrderViewSet.as_view({'get': 'filter_by_date'})),
    path('wishlist/move-to-cart/', WishlistViewSet.as_view({'post': 'move_to_cart'})),
    path('wishlist/bulk-delete/', WishlistViewSet.as_view({'post': 'bulk_delete'})),
    path('wishlist/stock-notifications/', WishlistViewSet.as_view({'get': 'stock_notifications'})),
    path('support/submit/', SupportTicketViewSet.as_view({'post': 'submit'})),

    path('', include(router.urls)),
]
urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
