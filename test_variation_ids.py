import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avantlush_backend.settings')
django.setup()

from api.models import Product
from api.serializers import ProductSerializer

# Test product 46 (the one you showed in the response)
try:
    product = Product.objects.get(id=46)
    serializer = ProductSerializer(product)
    data = serializer.data
    
    print('Product 46 variations:')
    for size_name, variation_data in data['variations'].items():
        variation_id = variation_data.get('variation_id', 'NOT FOUND')
        print(f'  {size_name}: variation_id = {variation_id}')
        
except Exception as e:
    print(f'Error: {e}')
