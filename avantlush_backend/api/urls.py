from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import waitlist_signup, preview_email, register, login, ProductViewSet, ArticleViewSet, CartViewSet, CartItemViewSet, OrderViewSet
from django.urls import path
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
    google_auth_callback
)
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'cart/items', CartItemViewSet, basename='cartitem')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('waitlist/signup/', waitlist_signup, name='waitlist_signup'),
    path('preview_email/', preview_email, name='preview_email'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path('auth/google/callback/', google_auth_callback, name='google_callback'),
    path('', include(router.urls)),
]
urlpatterns += router.urls
