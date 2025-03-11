# filters.py
from django_filters import rest_framework as filters
from django_filters import rest_framework as filters
from django.db.models import Q
from datetime import datetime
from .models import Product, Order


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

class OrderFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status')
    payment_status = filters.CharFilter(field_name='payment_status')
    customer = filters.CharFilter(method='filter_customer')
    date_from = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    min_total = filters.NumberFilter(field_name='total', lookup_expr='gte')
    max_total = filters.NumberFilter(field_name='total', lookup_expr='lte')

    class Meta:
        model = Order
        fields = ['status', 'payment_status', 'customer', 'date_from', 'date_to', 'min_total', 'max_total']

    def filter_customer(self, queryset, name, value):
        return queryset.filter(
            Q(user__email__icontains=value) |
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value)
        )