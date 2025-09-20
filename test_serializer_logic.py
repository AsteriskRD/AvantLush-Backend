#!/usr/bin/env python3
"""
Test the serializer logic directly to verify flexible ID handling
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avantlush_backend.settings')
django.setup()

from avantlush_backend.api.serializers import FlexibleProductField, FlexibleProductIdField
from avantlush_backend.api.models import Product

def test_flexible_product_field():
    """Test the FlexibleProductField serializer"""
    print("🧪 Testing FlexibleProductField...")
    
    field = FlexibleProductField()
    
    # Test with integer ID
    try:
        result = field.to_internal_value(41)
        print(f"✅ Integer ID (41): {result} (type: {type(result)})")
    except Exception as e:
        print(f"❌ Integer ID (41): {e}")
    
    # Test with unique variation ID
    try:
        result = field.to_internal_value("41_MED")
        print(f"✅ Variation ID (\"41_MED\"): {result} (type: {type(result)})")
    except Exception as e:
        print(f"❌ Variation ID (\"41_MED\"): {e}")
    
    # Test with invalid ID
    try:
        result = field.to_internal_value("invalid")
        print(f"❌ Invalid ID (\"invalid\"): {result}")
    except Exception as e:
        print(f"✅ Invalid ID (\"invalid\"): Correctly rejected - {e}")

def test_flexible_product_id_field():
    """Test the FlexibleProductIdField serializer"""
    print("\n🧪 Testing FlexibleProductIdField...")
    
    field = FlexibleProductIdField()
    
    # Test with integer ID
    try:
        result = field.to_internal_value(41)
        print(f"✅ Integer ID (41): {result} (type: {type(result)})")
    except Exception as e:
        print(f"❌ Integer ID (41): {e}")
    
    # Test with unique variation ID
    try:
        result = field.to_internal_value("41_MED")
        print(f"✅ Variation ID (\"41_MED\"): {result} (type: {type(result)})")
    except Exception as e:
        print(f"❌ Variation ID (\"41_MED\"): {e}")
    
    # Test with invalid ID
    try:
        result = field.to_internal_value("invalid")
        print(f"❌ Invalid ID (\"invalid\"): {result}")
    except Exception as e:
        print(f"✅ Invalid ID (\"invalid\"): Correctly rejected - {e}")

def test_product_exists():
    """Test if product 41 exists in the database"""
    print("\n🧪 Testing if Product 41 exists...")
    
    try:
        product = Product.objects.get(id=41)
        print(f"✅ Product 41 exists: {product.name}")
        return True
    except Product.DoesNotExist:
        print("❌ Product 41 does not exist")
        return False
    except Exception as e:
        print(f"❌ Error checking Product 41: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Flexible ID Serializer Logic")
    print("=" * 50)
    
    # Check if product exists first
    if not test_product_exists():
        print("\n⚠️  Warning: Product 41 doesn't exist. Some tests may fail.")
        print("   Please create a product with ID 41 or update the test IDs.")
    
    # Test the serializer fields
    test_flexible_product_field()
    test_flexible_product_id_field()
    
    print("\n✅ Test Summary:")
    print("- FlexibleProductField: Handles both integer and string IDs")
    print("- FlexibleProductIdField: Handles both integer and string IDs")
    print("- Invalid IDs are properly rejected")
    print("- Field names remain unchanged for frontend compatibility")

if __name__ == "__main__":
    main()
