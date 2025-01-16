from django.core.management.base import BaseCommand
from django.utils.text import slugify
from avantlush_backend.api.models import Category, Product
from decimal import Decimal
import uuid

class Command(BaseCommand):
    help = 'Populate the database with sample furniture products'

    def generate_sku(self, name):
        """Generate a unique SKU based on product name"""
        return f"CHAIR-{uuid.uuid4().hex[:8].upper()}"

    def handle(self, *args, **kwargs):
        # Create main category
        chairs_category, _ = Category.objects.get_or_create(
            name="Chairs",
            slug="chairs",
        )
        
        ergonomic_category, _ = Category.objects.get_or_create(
            name="Ergonomic Chairs",
            slug="ergonomic-chairs",
            parent=chairs_category
        )

        # Sample product data
        products = [
            {
                "name": "Modern Ergonomic Chair",
                "description": "Sleek modern ergonomic chair with white base and comfortable seating. Perfect for home office use with adjustable height and lumbar support.",
                "price": Decimal("299.99"),
                "images": [
                    "/media/products/modern-ergonomic-white.jpg",
                    "/media/products/modern-ergonomic-white-side.jpg"
                ],
                "stock_quantity": 50,
                "is_featured": True,
            },
            {
                "name": "Classic Red Designer Chair",
                "description": "Iconic red designer chair with wooden legs and ergonomic design. Combines style with comfort for a perfect accent piece.",
                "price": Decimal("199.99"),
                "images": [
                    "/media/products/classic-red-front.jpg",
                    "/media/products/classic-red-angle.jpg"
                ],
                "stock_quantity": 30,
                "is_featured": True,
            },
            {
                "name": "Executive Office Chair",
                "description": "Premium black leather executive office chair with adjustable features. Includes tilt mechanism and height adjustment.",
                "price": Decimal("399.99"),
                "images": [
                    "/media/products/executive-black-front.jpg",
                    "/media/products/executive-black-side.jpg"
                ],
                "stock_quantity": 20,
                "is_featured": False,
            },
            {
                "name": "Modern Dining Chair",
                "description": "Contemporary dining chair with elegant design and comfortable seating. Perfect for modern dining rooms.",
                "price": Decimal("159.99"),
                "images": [
                    "/media/products/dining-modern-front.jpg",
                    "/media/products/dining-modern-angle.jpg"
                ],
                "stock_quantity": 40,
                "is_featured": False,
            }
        ]

        # Create products
        for product_data in products:
            name = product_data["name"]
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "description": product_data["description"],
                    "price": product_data["price"],
                    "category": ergonomic_category,
                    "images": product_data["images"],
                    "stock_quantity": product_data["stock_quantity"],
                    "slug": slugify(name),
                    "is_featured": product_data["is_featured"],
                    "sku": self.generate_sku(name),
                    "status": "active"
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created product "{name}"')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Product "{name}" already exists')
                )