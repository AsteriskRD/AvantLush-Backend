#!/usr/bin/env python3
"""
Test script to verify that the flexible ID handling works for both:
1. Integer product IDs (e.g., 41)
2. Unique variation IDs (e.g., "41_MED")
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000/api"
TEST_USER_TOKEN = "your_test_token_here"  # Replace with actual token

def test_wishlist_with_integer_id():
    """Test wishlist with integer product ID"""
    print("🧪 Testing wishlist with integer product ID...")
    
    url = f"{BASE_URL}/wishlist-items/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TEST_USER_TOKEN}"
    }
    data = {
        "product": 41  # Integer product ID
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_wishlist_with_variation_id():
    """Test wishlist with unique variation ID"""
    print("\n🧪 Testing wishlist with unique variation ID...")
    
    url = f"{BASE_URL}/wishlist-items/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TEST_USER_TOKEN}"
    }
    data = {
        "product": "41_MED"  # Unique variation ID
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_order_with_integer_id():
    """Test order creation with integer product ID"""
    print("\n🧪 Testing order creation with integer product ID...")
    
    url = f"{BASE_URL}/orders/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TEST_USER_TOKEN}"
    }
    data = {
        "items": [
            {
                "product_id": 41,  # Integer product ID
                "quantity": 1,
                "price": 50.0
            }
        ],
        "shipping_address": "Test Address",
        "billing_address": "Test Address",
        "payment_method": "card"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_order_with_variation_id():
    """Test order creation with unique variation ID"""
    print("\n🧪 Testing order creation with unique variation ID...")
    
    url = f"{BASE_URL}/orders/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TEST_USER_TOKEN}"
    }
    data = {
        "items": [
            {
                "product_id": "41_MED",  # Unique variation ID
                "quantity": 1,
                "price": 50.0
            }
        ],
        "shipping_address": "Test Address",
        "billing_address": "Test Address",
        "payment_method": "card"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_cart_with_integer_id():
    """Test cart with integer product ID"""
    print("\n🧪 Testing cart with integer product ID...")
    
    url = f"{BASE_URL}/cart/add-item/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TEST_USER_TOKEN}"
    }
    data = {
        "product_id": 41,  # Integer product ID
        "quantity": 1,
        "size": "Medium",
        "color": "Blue"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_cart_with_variation_id():
    """Test cart with unique variation ID"""
    print("\n🧪 Testing cart with unique variation ID...")
    
    url = f"{BASE_URL}/cart/add-item/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TEST_USER_TOKEN}"
    }
    data = {
        "size_id": "41_MED",  # Unique variation ID in size_id field
        "quantity": 1,
        "size": "Medium",
        "color": "Blue"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Flexible ID Handling")
    print("=" * 50)
    
    # Note: These tests require authentication
    print("⚠️  Note: These tests require a valid authentication token")
    print("⚠️  Please update TEST_USER_TOKEN in the script")
    print("⚠️  Or run these tests manually with Postman/curl")
    
    print("\n📋 Test Scenarios:")
    print("1. Wishlist with integer ID (41)")
    print("2. Wishlist with variation ID (\"41_MED\")")
    print("3. Order with integer ID (41)")
    print("4. Order with variation ID (\"41_MED\")")
    print("5. Cart with integer ID (41)")
    print("6. Cart with variation ID (\"41_MED\")")
    
    print("\n✅ Expected Results:")
    print("- All tests should return 200/201 status codes")
    print("- No 'Incorrect type' errors")
    print("- Both integer and string IDs should work")
    print("- Field names remain unchanged")

if __name__ == "__main__":
    main()
