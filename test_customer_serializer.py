#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avantlush_backend.settings')
django.setup()

from avantlush_backend.api.models import Product
from avantlush_backend.api.serializers import ProductSerializer

def test_customer_serializer():
    # Get a product and test the customer-facing serializer
    product = Product.objects.first()
    if product:
        serializer = ProductSerializer(product)
        data = serializer.data
        print('Product ID:', product.id)
        print('Product Name:', product.name)
        print('Has final_price:', 'final_price' in data)
        print('Has variations:', 'variations' in data)
        print('Final price value:', data.get('final_price'))
        print('Variations value:', data.get('variations'))
        print('All fields:', list(data.keys()))
    else:
        print('No products found in database')

if __name__ == "__main__":
    test_customer_serializer()
