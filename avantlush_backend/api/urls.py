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
    WishlistViewSet, WishlistItemViewSet
    
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


# URL patterns for Django Rest Framework API
urlpatterns = [
    path('waitlist/signup/', waitlist_signup, name='waitlist_signup'),
    path('preview_email/', preview_email, name='preview_email'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path('auth/google/callback/', google_auth_callback, name='google_callback'),
#    path('auth/apple/', AppleLoginView.as_view(), name='apple_login'),
#    path('auth/apple/callback/', apple_auth_callback, name='apple_callback'),
    path('verify-email/<str:token>/<str:uidb64>/', verify_email, name='verify_email'),
    path('resend-verification/', resend_verification_email, name='resend_verification'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/<str:uidb64>/<str:token>/', reset_password, name='reset_password'),
    path('products/search/', ProductSearchView.as_view(), name='product-search'),
    path('products/<int:product_id>/recommendations/', ProductRecommendationView.as_view(), name='product-recommendations'),
    path('', include(router.urls)),
    path('', include(router.urls)),
]
urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)