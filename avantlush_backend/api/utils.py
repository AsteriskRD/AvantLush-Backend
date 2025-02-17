# utils.py

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