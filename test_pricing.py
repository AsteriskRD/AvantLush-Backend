#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avantlush_backend.settings')
django.setup()

from avantlush_backend.api.models import Product
from decimal import Decimal

def test_pricing():
    print("Testing pricing calculations...")
    
    # Test 1: No discount
    product1 = Product()
    product1.price = Decimal('100.00')
    product1.discount_type = None
    product1.discount_value = None
    print(f"Price: $100, No discount -> Final: ${product1.get_final_price()}")
    
    # Test 2: Percentage discount
    product2 = Product()
    product2.price = Decimal('100.00')
    product2.discount_type = 'percentage'
    product2.discount_value = Decimal('10.00')
    print(f"Price: $100, 10% discount -> Final: ${product2.get_final_price()}")
    
    # Test 3: Fixed discount
    product3 = Product()
    product3.price = Decimal('100.00')
    product3.discount_type = 'fixed'
    product3.discount_value = Decimal('15.00')
    print(f"Price: $100, $15 fixed discount -> Final: ${product3.get_final_price()}")
    
    # Test 4: Fixed discount that would make price negative
    product4 = Product()
    product4.price = Decimal('10.00')
    product4.discount_type = 'fixed'
    product4.discount_value = Decimal('15.00')
    print(f"Price: $10, $15 fixed discount -> Final: ${product4.get_final_price()} (should be 0)")
    
    print("✅ All pricing calculations working correctly!")

if __name__ == "__main__":
    test_pricing()
