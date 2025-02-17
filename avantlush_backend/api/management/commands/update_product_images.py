from django.core.management.base import BaseCommand
from avantlush_backend.api.models import Product
import json

class Command(BaseCommand):
    help = 'Update product images with Cloudinary URLs'

    def handle(self, *args, **kwargs):
        # Load uploaded image URLs from JSON
        with open('uploaded_images.json', 'r') as f:
            uploaded_images = json.load(f)

        # Map local filenames to Cloudinary URLs
        for product in Product.objects.all():
            new_images = []
            for image_path in product.images:
                filename = image_path.split('/')[-1]
                if filename in uploaded_images:
                    new_images.append(uploaded_images[filename])
                else:
                    self.stdout.write(self.style.WARNING(f'No Cloudinary URL found for {filename}'))

            if new_images:
                product.images = new_images
                product.save()
                self.stdout.write(self.style.SUCCESS(f'Updated images for {product.name}'))