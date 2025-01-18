# filters.py
from django_filters import rest_framework as filters

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