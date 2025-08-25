# utils.py

import uuid
import re
from django.db import models
from .models import Product, Category

VALID_COUNTRY_CODES = {
    '+1': 'United States/Canada',
    '+44': 'United Kingdom',
    '+61': 'Australia',
    '+64': 'New Zealand',
    '+27': 'South Africa',
    '+91': 'India',
    '+86': 'China',
    '+81': 'Japan',
    '+82': 'South Korea',
    '+55': 'Brazil',
    '+52': 'Mexico',
    '+234': 'Nigeria',
    '+233': 'Ghana',
    '+254': 'Kenya',
    '+971': 'UAE',
    '+966': 'Saudi Arabia',
    '+49': 'Germany',
    '+33': 'France',
    '+39': 'Italy',
    '+34': 'Spain',
    '+31': 'Netherlands',
    '+46': 'Sweden',
    '+47': 'Norway',
    '+45': 'Denmark',
    '+358': 'Finland'
}

def format_phone_number(country_code, phone_number):
    """
    Format phone number with country code and proper spacing
    """
    # Remove any existing formatting
    clean_number = ''.join(filter(str.isdigit, phone_number))
    
    # Remove country code if it's at the start of the phone number
    if clean_number.startswith(country_code[1:]):  # Remove '+' from country code
        clean_number = clean_number[len(country_code)-1:]
    
    # Format based on country code
    if country_code == '+1':  # US/Canada
        if len(clean_number) == 10:  # Standard North American format
            return f"{country_code} ({clean_number[:3]}) {clean_number[3:6]}-{clean_number[6:]}"
        elif len(clean_number) == 11 and clean_number.startswith('1'):  # With country code
            return f"{country_code} ({clean_number[1:4]}) {clean_number[4:7]}-{clean_number[7:]}"
        else:
            return f"{country_code} {clean_number}"  # Default format if not standard length
    elif country_code == '+44':  # UK
        return f"{country_code} {clean_number[:4]} {clean_number[4:6]} {clean_number[6:]}"
    else:
        # Default international format
        return f"{country_code} {clean_number}"

def validate_phone_format(country_code, phone_number):
    """
    Validate phone number format based on country code
    Returns (is_valid, error_message)
    """
    clean_number = ''.join(filter(str.isdigit, phone_number))
    
    if not country_code.startswith('+'):
        return False, "Country code must start with '+'"
    
    if country_code not in VALID_COUNTRY_CODES:
        return False, "Invalid country code"
    
    # Special validation for North America (US/Canada)
    if country_code == '+1':
        if len(clean_number) != 10 and not (len(clean_number) == 11 and clean_number.startswith('1')):
            return False, "North American numbers must be 10 digits (or 11 with leading '1')"
    else:
        # Length validation for other countries
        min_length = 9
        max_length = 15
        
        if len(clean_number) < min_length or len(clean_number) > max_length:
            return False, f"Phone number must be between {min_length} and {max_length} digits"
    
    return True, None

def generate_sku(product_name, category=None, existing_sku=None):
    """
    Generate a unique SKU for a product
    
    Args:
        product_name (str): The name of the product
        category (Category, optional): The product category
        existing_sku (str, optional): Existing SKU to check for uniqueness
    
    Returns:
        str: A unique SKU
    """
    # Get category prefix
    if category:
        # Extract first 3-4 letters from category name
        category_prefix = re.sub(r'[^A-Za-z]', '', category.name)[:4].upper()
    else:
        category_prefix = "PROD"
    
    # Clean product name and get first 2-3 meaningful words
    words = re.sub(r'[^A-Za-z\s]', '', product_name).split()
    if len(words) >= 2:
        product_prefix = ''.join(word[:2].upper() for word in words[:2])
    else:
        product_prefix = words[0][:4].upper() if words else "ITEM"
    
    # Generate unique identifier
    unique_id = uuid.uuid4().hex[:6].upper()
    
    # Create SKU format: CAT-PROD-UNIQUEID
    sku = f"{category_prefix}-{product_prefix}-{unique_id}"
    
    # Ensure uniqueness
    counter = 1
    original_sku = sku
    while Product.objects.filter(sku=sku).exclude(sku=existing_sku).exists():
        sku = f"{original_sku}-{counter:02d}"
        counter += 1
        if counter > 99:  # Prevent infinite loop
            # Fallback to timestamp-based SKU
            import time
            timestamp = int(time.time()) % 1000000
            sku = f"{category_prefix}-{timestamp:06d}"
            break
    
    return sku

def generate_sku_from_category(category_name, product_name):
    """
    Generate SKU based on category name and product name
    
    Args:
        category_name (str): Category name
        product_name (str): Product name
    
    Returns:
        str: Generated SKU
    """
    # Clean category name and get prefix
    category_prefix = re.sub(r'[^A-Za-z]', '', category_name)[:4].upper()
    
    # Clean product name and get meaningful prefix
    words = re.sub(r'[^A-Za-z\s]', '', product_name).split()
    if len(words) >= 2:
        product_prefix = ''.join(word[:2].upper() for word in words[:2])
    else:
        product_prefix = words[0][:4].upper() if words else "ITEM"
    
    # Generate unique identifier
    unique_id = uuid.uuid4().hex[:6].upper()
    
    return f"{category_prefix}-{product_prefix}-{unique_id}"

def is_sku_unique(sku, exclude_product_id=None):
    """
    Check if a SKU is unique
    
    Args:
        sku (str): SKU to check
        exclude_product_id (int, optional): Product ID to exclude from check
    
    Returns:
        bool: True if SKU is unique, False otherwise
    """
    queryset = Product.objects.filter(sku=sku)
    if exclude_product_id:
        queryset = queryset.exclude(id=exclude_product_id)
    return not queryset.exists()