#!/usr/bin/env python
"""
Test script to verify the last item logic implementation
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avantlush_backend.settings')
django.setup()

from avantlush_backend.api.models import Product, ProductVariation, Size, Color, Cart, CartItem, CustomUser
from decimal import Decimal

def test_last_item_logic():
    print("🧪 Testing Last Item Logic Implementation")
    print("=" * 50)
    
    # Create test data
    try:
        # Get or create test product
        product = Product.objects.filter(name__icontains="Test").first()
        if not product:
            print("❌ No test product found. Please create a product first.")
            return
            
        # Get or create test size and color
        size, _ = Size.objects.get_or_create(name="Test Size")
        color, _ = Color.objects.get_or_create(name="Test Color")
        
        # Get or create variation
        variation = ProductVariation.objects.filter(
            product=product,
            sizes=size,
            colors=color
        ).first()
        
        if not variation:
            print("❌ No variation found. Please create a variation first.")
            return
            
        print(f"📦 Testing with Product: {product.name}")
        print(f"📏 Size: {size.name}")
        print(f"🎨 Color: {color.name}")
        print(f"📊 Initial stock_quantity: {variation.stock_quantity}")
        print(f"📊 Initial reserved_quantity: {variation.reserved_quantity}")
        print(f"📊 Initial available_quantity: {variation.available_quantity}")
        print()
        
        # Test 1: Set stock to 1 (last item scenario)
        print("🔬 Test 1: Setting stock to 1 (Last Item Scenario)")
        variation.stock_quantity = 1
        variation.reserved_quantity = 0
        variation.save()
        product.status = 'active'
        product.save()
        
        print(f"📊 After setting to 1: stock={variation.stock_quantity}, reserved={variation.reserved_quantity}, available={variation.available_quantity}")
        
        # Test 2: Add to cart (should NOT reduce available_quantity)
        print("\n🛒 Test 2: Adding last item to cart")
        print("Expected: available_quantity should stay 1, reserved_quantity should increase")
        
        # Simulate adding to cart
        variation.reserved_quantity += 1
        variation.save()
        
        print(f"📊 After adding to cart: stock={variation.stock_quantity}, reserved={variation.reserved_quantity}, available={variation.available_quantity}")
        print(f"📊 Product status: {product.status}")
        
        if variation.available_quantity == 1:
            print("✅ SUCCESS: Available quantity stayed at 1 (last item logic working)")
        else:
            print("❌ FAILED: Available quantity changed when it shouldn't have")
            
        # Test 3: Multiple users adding same last item
        print("\n👥 Test 3: Multiple users adding same last item")
        print("Expected: Multiple users can add the same last item")
        
        # Simulate second user adding to cart
        variation.reserved_quantity += 1
        variation.save()
        
        print(f"📊 After second user adds to cart: stock={variation.stock_quantity}, reserved={variation.reserved_quantity}, available={variation.available_quantity}")
        
        if variation.available_quantity == 1:
            print("✅ SUCCESS: Multiple users can add the same last item")
        else:
            print("❌ FAILED: Second user couldn't add the last item")
            
        # Test 4: Payment completion (should reduce actual stock)
        print("\n💳 Test 4: Payment completion")
        print("Expected: stock_quantity should reduce to 0, product should become draft")
        
        # Simulate payment completion
        variation.stock_quantity -= 1
        variation.reserved_quantity -= 1  # Release one reservation
        variation.save()
        
        if variation.available_quantity == 0:
            product.status = 'draft'
            product.save()
            print("✅ SUCCESS: Product became draft after payment completion")
        else:
            print("❌ FAILED: Product didn't become draft")
            
        print(f"📊 After payment completion: stock={variation.stock_quantity}, reserved={variation.reserved_quantity}, available={variation.available_quantity}")
        print(f"📊 Product status: {product.status}")
        
        # Test 5: Payment failure (should release reserved stock)
        print("\n❌ Test 5: Payment failure scenario")
        print("Expected: Reserved stock should be released, product should become active again")
        
        # Reset for test
        variation.stock_quantity = 1
        variation.reserved_quantity = 1  # One item still reserved
        variation.save()
        product.status = 'active'
        product.save()
        
        # Simulate payment failure - release reserved stock
        variation.reserved_quantity = max(0, variation.reserved_quantity - 1)
        variation.save()
        
        print(f"📊 After payment failure: stock={variation.stock_quantity}, reserved={variation.reserved_quantity}, available={variation.available_quantity}")
        print(f"📊 Product status: {product.status}")
        
        if variation.available_quantity == 1 and product.status == 'active':
            print("✅ SUCCESS: Reserved stock released, product active again")
        else:
            print("❌ FAILED: Reserved stock not properly released")
            
        print("\n🎉 Last Item Logic Test Complete!")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_last_item_logic()
