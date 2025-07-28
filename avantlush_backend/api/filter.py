# filters.py
import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q
from datetime import datetime
from .models import Product, Order, OrderItem


class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    category = filters.CharFilter(field_name='category__slug')
    rating = filters.NumberFilter(field_name='rating', lookup_expr='gte')
    search = filters.CharFilter(method='search_filter')

    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'category', 'rating']

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )


class OrderFilter(django_filters.FilterSet):
    # Status filtering for the tabs (All, Processing, Delivered, Cancelled)
    status = django_filters.ChoiceFilter(choices=Order.STATUS_CHOICES)
    
    # Date filtering for the date picker
    date = django_filters.DateFilter(field_name='created_at__date', lookup_expr='exact')
    start_date = django_filters.DateFilter(field_name='created_at__date', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='created_at__date', lookup_expr='lte')
    date_range = django_filters.DateFromToRangeFilter(field_name='created_at__date')
    
    # Customer search (for filtering by customer name/email)
    customer = django_filters.CharFilter(method='filter_customer')
    customer_email = django_filters.CharFilter(field_name='user__email', lookup_expr='icontains')
    customer_name = django_filters.CharFilter(method='filter_customer_name')
    
    # Order ID search
    order_id = django_filters.CharFilter(field_name='id', lookup_expr='icontains')
    
    # Product search (for filtering by product name)
    product = django_filters.CharFilter(method='filter_product')
    
    # Payment method filtering (Mastercard, Visa, PayPal, etc.)
    payment_type = django_filters.CharFilter(field_name='payment_type', lookup_expr='iexact')
    
    # Total amount filtering
    min_total = django_filters.NumberFilter(field_name='total', lookup_expr='gte')
    max_total = django_filters.NumberFilter(field_name='total', lookup_expr='lte')
    
    # Search across multiple fields
    search = django_filters.CharFilter(method='global_search')
    
    class Meta:
        model = Order
        fields = [
            'status', 'date', 'start_date', 'end_date', 'customer', 
            'customer_email', 'customer_name', 'order_id', 'product',
            'payment_type', 'min_total', 'max_total', 'search'
        ]
    
    def filter_customer(self, queryset, name, value):
        """Filter by customer name or email"""
        return queryset.filter(
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value) |
            Q(user__email__icontains=value)
        )
    
    def filter_customer_name(self, queryset, name, value):
        """Filter specifically by customer name"""
        return queryset.filter(
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value)
        )
    
    def filter_product(self, queryset, name, value):
        """Filter by product name"""
        return queryset.filter(
            Q(items__product__name__icontains=value)
        ).distinct()
    
    def global_search(self, queryset, name, value):
        """Global search across order ID, customer, and product"""
        return queryset.filter(
            Q(id__icontains=value) |
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value) |
            Q(user__email__icontains=value) |
            Q(items__product__name__icontains=value)
        ).distinct()