#!/usr/bin/env python3
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avantlush_backend.settings')
django.setup()

from api.models import Product
from api.serializers import ProductSerializer

def test_customer_api_response():
    """Test what the customer-facing API returns for variations and final_price"""
    
    # Get a product that has variations
    product = Product.objects.filter(variations__isnull=False).first()
    
    if not product:
        print("❌ No products with variations found")
        return
    
    print(f"✅ Testing product: {product.name}")
    print(f"   Product ID: {product.id}")
    print(f"   Base Price: ${product.price}")
    print(f"   Discount Type: {product.discount_type}")
    print(f"   Discount Value: {product.discount_value}")
    print()
    
    # Test the customer-facing serializer
    serializer = ProductSerializer(product)
    data = serializer.data
    
    print("🔍 Customer API Response:")
    print(f"   final_price: {data.get('final_price', 'NOT FOUND')}")
    print(f"   variations: {data.get('variations', 'NOT FOUND')}")
    print()
    
    # Check if variations exist
    variations = data.get('variations', {})
    if variations:
        print("📋 Variations Details:")
        for size, details in variations.items():
            print(f"   Size: {size}")
            print(f"     - size_id: {details.get('size_id')}")
            print(f"     - colors: {details.get('colors')}")
            print(f"     - price: ${details.get('price')}")
            print(f"     - stock_quantity: {details.get('stock_quantity')}")
            print()
    else:
        print("❌ No variations found in response")
    
    # Check final_price calculation
    final_price = data.get('final_price')
    if final_price:
        print(f"💰 Final Price Calculation:")
        print(f"   Base Price: ${product.price}")
        print(f"   Final Price: ${final_price}")
        print(f"   Discount Applied: {product.discount_type} - {product.discount_value}")
    else:
        print("❌ No final_price found in response")

if __name__ == "__main__":
    test_customer_api_response()
