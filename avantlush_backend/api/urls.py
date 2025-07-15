from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    waitlist_signup,
    preview_email,
    register,
    login,
    verify_email,
    resend_verification_email,
    forgot_password,
    reset_password,
    GoogleLoginView,
    ProductViewSet,
    ArticleViewSet,
    CartViewSet,
    CartItemViewSet,
    OrderViewSet,
    WishlistViewSet,
    WishlistItemViewSet,
    CheckoutViewSet,
    # SupportTicketViewSet,  # 🚫 COMMENTED OUT: Not implemented yet
    ProfileViewSet,
    AddressViewSet,
    ProductSearchView,
    ProductRecommendationView,
    RecordProductViewView,
    ReviewViewSet,
    DashboardViewSet,
    CustomerViewSet,
    ProductReviewViewSet,
    TokenValidationView,
    CarouselViewSet,
    admin_login,
    check_admin_access,
    OrderCreateView,
    OrderUpdateView,
    order_choices,
    ProductDetailForOrderView,
    CustomerListView,
    ColorViewSet,
    SizeViewSet,
    clover_hosted_webhook,
    clover_hosted_payment_status,
    order_payments_list,
    payment_methods,
    create_checkout_session,
    test_complete_checkout,
    create_clover_hosted_checkout,
    create_clover_hosted_checkout_test,  # 🔧 ADD: Import test function
    refresh_user_orders,  # 🔧 ADD: Import refresh function
    checkout_success,
    checkout_failure,
    checkout_cancel,
    checkout_status_api,
)

# Router setup
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
# router.register(r'shipping-methods', ShippingMethodViewSet, basename='shipping-method')  # 🚫 COMMENTED OUT: Not implemented yet
# router.register(r'help', SupportTicketViewSet, basename='help')  # 🚫 COMMENTED OUT: Not implemented yet
router.register(r'checkout', CheckoutViewSet, basename='checkout')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'product-management', ProductViewSet, basename='product-management')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'products/(?P<product_id>\d+)/reviews', ProductReviewViewSet, basename='product-reviews')
router.register(r'carousel', CarouselViewSet, basename='carousel')
router.register(r'colors', ColorViewSet, basename='color')
router.register(r'sizes', SizeViewSet, basename='size')

# URL patterns
urlpatterns = [
    # Authentication & User Management
    path('waitlist/signup/', waitlist_signup, name='waitlist_signup'),
    path('preview_email/', preview_email, name='preview_email'),
    path('register/', register, name='register'),
    path('auth/', include('dj_rest_auth.urls')),  # This includes login, logout, user details, etc.
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path('verify-email/<str:token>/<str:uidb64>/', verify_email, name='verify_email'),
    path('resend-verification/', resend_verification_email, name='resend_verification'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/<str:uidb64>/<str:token>/', reset_password, name='reset_password'),
    path('auth/validate-token/', TokenValidationView.as_view(), name='validate-token'),

    # 🔧 CLOVER CHECKOUT ENDPOINTS - MOVED TO TOP
    # PRODUCTION: Requires authentication
    path('create-hosted-checkout/', create_clover_hosted_checkout, name='create-hosted-checkout'),
    
    # 🔧 NEW: TESTING: No authentication required (for development)
    path('create-hosted-checkout-test/', create_clover_hosted_checkout_test, name='create-hosted-checkout-test'),
    
    # 🔧 NEW: Order refresh endpoint
    path('orders/refresh/', refresh_user_orders, name='refresh-user-orders'),

    path('test-complete-checkout/', test_complete_checkout, name='test-complete-checkout'),

    # Product & Wishlist
    path('products/search/', ProductSearchView.as_view(), name='product-search'),
    path('wishlist-items/<int:product_id>/remove/', WishlistItemViewSet.as_view({'delete': 'remove_by_product_id'})),

    # NEW: Product View Recording
    path('products/record-view/', RecordProductViewView.as_view(), name='record-product-view'),

    # Product Recommendations
    path('products/<int:product_id>/recommendations/',
         ProductRecommendationView.as_view(),
         name='product-recommendations'),
    path('products/<int:product_id>/recommendations/<str:rec_type>/',
         ProductRecommendationView.as_view(),
         name='product-recommendations-by-type'),

    # Carousel Products Images
    path('carousel/public/', CarouselViewSet.as_view({'get': 'public'}), name='carousel-public'),
    path('carousel/reorder/', CarouselViewSet.as_view({'post': 'reorder'}), name='carousel-reorder'),

    path('wishlist/move-to-cart/<int:pk>/', WishlistViewSet.as_view({'post': 'move_to_cart'})),
    path('wishlist/bulk-delete/', WishlistViewSet.as_view({'post': 'bulk_delete'})),
    path('wishlist/stock-notifications/', WishlistViewSet.as_view({'get': 'stock_notifications'})),
    path('products/export/', ProductViewSet.as_view({'get': 'export'}), name='product-export'),
    path('products/bulk-update-status/', ProductViewSet.as_view({'post': 'bulk_update_status'}), name='product-bulk-update'),

    ## DASHBOARD
    path('products/<int:pk>/upload-image/',
        ProductViewSet.as_view({'post': 'upload-image'}),
        name='product-upload-image'),
    path('products/<int:pk>/remove-image/<str:image_id>/',
        ProductViewSet.as_view({'delete': 'remove-image'}),
        name='product-remove-image'),
    path('products/tags/',
        ProductViewSet.as_view({'get': 'tags'}),
        name='product-tags'),
    path('products/categories/',
        ProductViewSet.as_view({'get': 'categories'}),
        name='product-categories'),
    path('admin/login/', admin_login, name='admin-login'),
    path('admin/check-access/', check_admin_access, name='check-admin-access'),

    # Cart Management
    path('cart/summary/', CartViewSet.as_view({'get': 'summary'})),
    path('cart/add-item/', CartViewSet.as_view({'post': 'add_item'})),
    path('cart/update-quantity/', CartViewSet.as_view({'post': 'update_quantity'})),
    path('cart/remove-item/', CartViewSet.as_view({'post': 'remove_item'})),
    path('cart/apply-discount/', CartViewSet.as_view({'post': 'apply_discount'})),
    path('cart/clear/', CartViewSet.as_view({'post': 'clear'})),

    # Orders & Tracking
    path('orders/<int:pk>/tracking/', OrderViewSet.as_view({'get': 'tracking_history'})),
    path('orders/<int:pk>/tracking/add/', OrderViewSet.as_view({'post': 'add_tracking_event'})),
    path('orders/filter-by-date/', OrderViewSet.as_view({'get': 'filter_by_date'})),

    path('api/orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('api/orders/<int:pk>/update/', OrderUpdateView.as_view(), name='order-update'),
    path('api/orders/choices/', order_choices, name='order-choices'),
    path('api/products/<int:pk>/for-order/', ProductDetailForOrderView.as_view(), name='product-for-order'),
    path('api/customers/list/', CustomerListView.as_view(), name='customer-list'),

    # Additional Order Management Endpoints
    path('orders/export/', OrderViewSet.as_view({'get': 'export'}), name='order-export'),
    path('orders/summary/', OrderViewSet.as_view({'get': 'summary'}), name='order-summary'),
    path('orders/flat/', OrderViewSet.as_view({'get': 'flat_orders'}), name='flat-orders'),
    path('orders/bulk-action/', OrderViewSet.as_view({'post': 'bulk_action'}), name='bulk-action'),

    # Clover url configuration
    path('checkout/clover-hosted/create/',
         CheckoutViewSet.as_view({'post': 'create_clover_hosted_checkout'}),
         name='clover-hosted-checkout-create'),

    path('checkout/clover-hosted/status/<int:order_id>/',
         clover_hosted_payment_status,
         name='clover-hosted-payment-status'),

    # Clover redirect handlers
    path('checkout/success/', checkout_success, name='checkout-success'),
    path('checkout/failure/', checkout_failure, name='checkout-failure'),
    path('checkout/cancel/', checkout_cancel, name='checkout-cancel'),

    # API endpoint for status checking
    path('api/checkout/status/', checkout_status_api, name='checkout-status-api'),

    # Webhooks
    path('webhooks/clover-hosted/',
         clover_hosted_webhook,
         name='clover-hosted-webhook'),

    # Support & Checkout
    path('support/submit/', SupportTicketViewSet.as_view({'post': 'submit'})),
    path('checkout/payment_methods/', payment_methods, name='checkout-payment-methods'),
    path('checkout/payment-methods/', payment_methods, name='checkout-payment-methods-alt'),
    path('checkout/create-session/', create_checkout_session, name='checkout-create-session'),

    # External App URLs
    path('api/', include('checkout.urls')),

    # Include router-based URLs AT THE END
    path('', include(router.urls)),
]

# Serve media files in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)