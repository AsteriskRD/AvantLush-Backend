#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avantlush_backend.settings')
django.setup()

from avantlush_backend.api.models import Product, ProductVariation, Size

def debug_product_variations():
    try:
        product = Product.objects.get(id=21)
        print('=== PRODUCT VARIATIONS ===')
        for v in product.variations.all():
            print(f'Variation ID: {v.id}')
            print(f'Variation field: {v.variation}')
            print(f'Sizes: {[s.name for s in v.sizes.all()]}')
            print(f'Size FK: {v.size.name if v.size else None}')
            print(f'Colors: {[c.name for c in v.colors.all()]}')
            print('---')
        
        print('=== ALL SIZES ===')
        for s in Size.objects.all():
            print(f'Size ID: {s.id}, Name: {s.name}')
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_product_variations()
