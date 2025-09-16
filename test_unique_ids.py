import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avantlush_backend.settings')
django.setup()

from api.models import Product
from api.serializers import ProductSerializer

# Test product 46
try:
    product = Product.objects.get(id=46)
    serializer = ProductSerializer(product)
    data = serializer.data
    
    print('Product 46 variations:')
    for size_name, variation_data in data['variations'].items():
        size_id = variation_data.get('size_id')
        print(f'  {size_name}: size_id = {size_id} (type: {type(size_id)})')
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
