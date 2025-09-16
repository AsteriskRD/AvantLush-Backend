#!/usr/bin/env python
"""
Test script to verify if custom size variations are working on Render
"""
import requests
import json

def test_render_deployment():
    # Replace with your actual Render URL
    RENDER_URL = "https://avantlush-backend-2s6k.onrender.com"
    
    print("🧪 Testing Render Deployment...")
    print(f"URL: {RENDER_URL}")
    
    # Test 1: Check if the API is responding
    try:
        response = requests.get(f"{RENDER_URL}/api/products/21/", timeout=10)
        print(f"✅ API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Product Name: {data.get('data', {}).get('name', 'N/A')}")
            
            # Check variations
            variations = data.get('data', {}).get('variations', {})
            print(f"📊 Variations Found: {len(variations)}")
            
            for size_name, var_data in variations.items():
                print(f"  - Size: {size_name}")
                print(f"    Colors: {var_data.get('colors', [])}")
                print(f"    Price: ${var_data.get('price', 0)}")
                print(f"    Stock: {var_data.get('stock_quantity', 0)}")
            
            # Check if we have custom sizes
            custom_sizes = [size for size in variations.keys() if size in ['X', 'M', 'L', 'XL', 'XXL', 'S']]
            if custom_sizes:
                print(f"🎉 Custom sizes found: {custom_sizes}")
            else:
                print("❌ No custom sizes found")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    test_render_deployment()
