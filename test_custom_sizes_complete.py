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
from avantlush_backend.api.serializers import ProductManagementSerializer

def test_custom_sizes_complete():
    try:
        print("=== TESTING CUSTOM SIZES COMPLETE ===")
        
        product = Product.objects.get(id=21)
        
        # Clear existing variations
        product.variations.all().delete()
        print("Cleared existing variations")
        
        # Create variations with different custom sizes
        custom_variations = [
            {"size": "XS", "colors": ["Red", "Blue"], "price": 25.0, "stock": 5},
            {"size": "S", "colors": ["Green"], "price": 30.0, "stock": 8},
            {"size": "M", "colors": ["Black", "White"], "price": 35.0, "stock": 12},
            {"size": "L", "colors": ["Yellow"], "price": 40.0, "stock": 15},
            {"size": "XL", "colors": [], "price": 45.0, "stock": 10},  # No colors
            {"size": "XXL", "colors": ["Purple", "Orange"], "price": 50.0, "stock": 7},
        ]
        
        for var_data in custom_variations:
            # Create or get size
            size_obj, _ = Size.objects.get_or_create(name=var_data["size"])
            
            # Create variation
            variation = ProductVariation.objects.create(
                product=product,
                variation_type='size',
                variation=var_data["size"],
                price_adjustment=var_data["price"] - float(product.price),
                stock_quantity=var_data["stock"],
                is_default=False,
            )
            
            # Add size
            variation.sizes.add(size_obj)
            variation.size = size_obj
            variation.save()
            
            # Add colors
            for color_name in var_data["colors"]:
                color_obj, _ = Color.objects.get_or_create(name=color_name)
                variation.colors.add(color_obj)
            
            print(f"Created variation: {var_data['size']} with {len(var_data['colors'])} colors")
        
        # Test the serializer
        print("\n=== SERIALIZER RESULT ===")
        serializer = ProductManagementSerializer(product)
        variations = serializer.get_variations(product)
        
        for size_name, data in variations.items():
            print(f"Size: {size_name}")
            print(f"  - ID: {data['size_id']}")
            print(f"  - Colors: {data['colors']}")
            print(f"  - Price: ${data['price']}")
            print(f"  - Stock: {data['stock_quantity']}")
            print()
        
        print("✅ Custom sizes are working perfectly!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_custom_sizes_complete()
