from django.core.management.base import BaseCommand
from avantlush_backend.api.models import Product

class Command(BaseCommand):
    help = 'Update product images with Cloudinary URLs'

    def handle(self, *args, **kwargs):
        image_mapping = {
            "Modern Ergonomic Chair": ["Egonomic chair2.jpg"],
            "Classic Red Designer Chair": ["Chair.jpg"],
            "Executive Office Chair": ["single chair.jpg"],
            "Modern Dining Chair": ["three seater.jpg"],
            "Elegant Marble Dining Table": ["dinnig table.jpg"],
            "Industrial Wood Dining Table": ["dinnig table2.jpg"],
            "Minimalist Glass Coffee Table": ["centertable.jpg"],
            "Wooden Round Coffee Table": ["table.jpg"],
            "Modern Pendant Light": ["lampstand.jpg"],
            "Modern TV Console": ["tv console.jpg", "tv console2.jpg", "Tv console3.jpg", "tv console4.jpg", "Tv console5.jpg"],
            "Storage Ottoman": ["bedside.jpg"],
            "LED Wall Sconce": ["flowervase.jpg"],
            "Geometric Table Lamp": ["frontdesk table.jpg"]
        }

        for name, new_images in image_mapping.items():
            try:
                product = Product.objects.get(name=name)
                # Update the JSONField images
                product.images = new_images
                
                # Set main image to first image if available
                if new_images:
                    product.main_image = new_images[0]
                
                product.save()
                self.stdout.write(self.style.SUCCESS(f'Updated images for "{name}"'))
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Product "{name}" not found'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating "{name}": {str(e)}'))