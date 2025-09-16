import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avantlush_backend.settings')
django.setup()

from avantlush_backend.api.models import Product
from avantlush_backend.api.serializers import ProductSerializer

product = Product.objects.get(id=46)
serializer = ProductSerializer(product)
data = serializer.data

print('Product 46 variations:')
for size_name, variation_data in data['variations'].items():
    size_id = variation_data.get('size_id')
    print(f'  {size_name}: size_id = {size_id}')
