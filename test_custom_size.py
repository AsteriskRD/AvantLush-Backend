#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avantlush_backend.settings')
django.setup()

from avantlush_backend.api.models import Product, ProductVariation, Size, Color

def test_custom_size_creation():
    try:
        print("=== TESTING CUSTOM SIZE CREATION ===")
        
        # Test creating custom sizes
        custom_sizes = ["X", "XX", "M", "L", "XL", "S"]
        
        for size_name in custom_sizes:
            size_obj, created = Size.objects.get_or_create(name=size_name)
            print(f"Size '{size_name}': ID={size_obj.id}, Created={created}")
        
        print("\n=== ALL SIZES AFTER CREATION ===")
        for s in Size.objects.all().order_by('id'):
            print(f"Size ID: {s.id}, Name: '{s.name}'")
            
        # Test creating a variation with custom size
        print("\n=== TESTING VARIATION WITH CUSTOM SIZE ===")
        product = Product.objects.get(id=21)
        
        # Clear existing variations first
        product.variations.all().delete()
        print("Cleared existing variations")
        
        # Create a variation with size "X"
        size_x = Size.objects.get(name="X")
        variation = ProductVariation.objects.create(
            product=product,
            variation_type='size',
            variation='X',
            price_adjustment=0,
            stock_quantity=10,
            is_default=False,
        )
        
        # Add the size
        variation.sizes.add(size_x)
        variation.size = size_x  # legacy FK
        variation.save()
        
        print(f"Created variation: ID={variation.id}, Size='{variation.size.name}'")
        
        # Test the serializer's get_variations method
        print("\n=== TESTING SERIALIZER OUTPUT ===")
        from avantlush_backend.api.serializers import ProductManagementSerializer
        
        serializer = ProductManagementSerializer(product)
        variations = serializer.get_variations(product)
        print(f"Serializer variations: {variations}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_custom_size_creation()
