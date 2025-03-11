from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CheckoutViewSet

router = DefaultRouter()
router.register(r'checkout', CheckoutViewSet, basename='checkout')

urlpatterns = [
    path('', include(router.urls)),
]