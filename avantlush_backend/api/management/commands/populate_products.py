from django.core.management.base import BaseCommand
from django.utils.text import slugify
from avantlush_backend.api.models import Category, Product
from decimal import Decimal
import uuid

class Command(BaseCommand):
    help = 'Populate the database with sample furniture products'

    def generate_sku(self, name, category_prefix):
        """Generate a unique SKU based on product name and category"""
        return f"{category_prefix}-{uuid.uuid4().hex[:8].upper()}"

    def handle(self, *args, **kwargs):
        # Create main categories
        chairs_category, _ = Category.objects.get_or_create(
            name="Chairs",
            slug="chairs",
        )
        
        tables_category, _ = Category.objects.get_or_create(
            name="Tables",
            slug="tables",
        )

        lighting_category, _ = Category.objects.get_or_create(
            name="Lighting",
            slug="lighting",
        )

        storage_category, _ = Category.objects.get_or_create(
            name="Storage",
            slug="storage",
        )

        decor_category, _ = Category.objects.get_or_create(
            name="Home Decor",
            slug="home-decor",
        )

        # Create subcategories
        ergonomic_category, _ = Category.objects.get_or_create(
            name="Ergonomic Chairs",
            slug="ergonomic-chairs",
            parent=chairs_category
        )

        dining_chairs_category, _ = Category.objects.get_or_create(
            name="Dining Chairs",
            slug="dining-chairs",
            parent=chairs_category
        )

        dining_tables_category, _ = Category.objects.get_or_create(
            name="Dining Tables",
            slug="dining-tables",
            parent=tables_category
        )

        coffee_tables_category, _ = Category.objects.get_or_create(
            name="Coffee Tables",
            slug="coffee-tables",
            parent=tables_category
        )

        # Sample product data
        products = [
            # Original Chair Products
            {
                "name": "Modern Ergonomic Chair",
                "description": "Sleek modern ergonomic chair with white base and comfortable seating. Perfect for home office use with adjustable height and lumbar support.",
                "price": Decimal("299.99"),
                "images": ["/media/products/modern-ergonomic-white.jpg", "/media/products/modern-ergonomic-white-side.jpg"],
                "stock_quantity": 50,
                "is_featured": True,
                "category": ergonomic_category,
                "sku_prefix": "CHAIR"
            },
            {
                "name": "Classic Red Designer Chair",
                "description": "Iconic red designer chair with wooden legs and ergonomic design. Combines style with comfort for a perfect accent piece.",
                "price": Decimal("199.99"),
                "images": ["/media/products/classic-red-front.jpg", "/media/products/classic-red-angle.jpg"],
                "stock_quantity": 30,
                "is_featured": True,
                "category": ergonomic_category,
                "sku_prefix": "CHAIR"
            },
            {
                "name": "Executive Office Chair",
                "description": "Premium black leather executive office chair with adjustable features. Includes tilt mechanism and height adjustment.",
                "price": Decimal("399.99"),
                "images": ["/media/products/executive-black-front.jpg", "/media/products/executive-black-side.jpg"],
                "stock_quantity": 20,
                "is_featured": False,
                "category": ergonomic_category,
                "sku_prefix": "CHAIR"
            },
            {
                "name": "Modern Dining Chair",
                "description": "Contemporary dining chair with elegant design and comfortable seating. Perfect for modern dining rooms.",
                "price": Decimal("159.99"),
                "images": ["/media/products/dining-modern-front.jpg", "/media/products/dining-modern-angle.jpg"],
                "stock_quantity": 40,
                "is_featured": False,
                "category": dining_chairs_category,
                "sku_prefix": "DCHAIR"
            },
            # New Dining Tables
            {
                "name": "Elegant Marble Dining Table",
                "description": "Luxurious marble-top dining table with brass-finished steel base. Seats 6-8 people comfortably.",
                "price": Decimal("1299.99"),
                "images": ["/media/products/marble-dining-table.jpg", "/media/products/marble-dining-detail.jpg"],
                "stock_quantity": 10,
                "is_featured": True,
                "category": dining_tables_category,
                "sku_prefix": "TABLE"
            },
            {
                "name": "Industrial Wood Dining Table",
                "description": "Rustic solid wood dining table with metal frame. Perfect for modern industrial interiors.",
                "price": Decimal("899.99"),
                "images": ["/media/products/industrial-dining-table.jpg", "/media/products/industrial-dining-detail.jpg"],
                "stock_quantity": 15,
                "is_featured": False,
                "category": dining_tables_category,
                "sku_prefix": "TABLE"
            },
            # Coffee Tables
            {
                "name": "Minimalist Glass Coffee Table",
                "description": "Modern glass coffee table with chrome frame. Sleek and sophisticated design.",
                "price": Decimal("449.99"),
                "images": ["/media/products/glass-coffee-table.jpg", "/media/products/glass-coffee-detail.jpg"],
                "stock_quantity": 25,
                "is_featured": True,
                "category": coffee_tables_category,
                "sku_prefix": "CTABLE"
            },
            {
                "name": "Wooden Round Coffee Table",
                "description": "Natural wood round coffee table with storage shelf. Scandinavian-inspired design.",
                "price": Decimal("349.99"),
                "images": ["/media/products/round-coffee-table.jpg", "/media/products/round-coffee-detail.jpg"],
                "stock_quantity": 20,
                "is_featured": False,
                "category": coffee_tables_category,
                "sku_prefix": "CTABLE"
            },
            # Lighting
            {
                "name": "Modern Pendant Light",
                "description": "Contemporary pendant light with adjustable height. Perfect for dining areas.",
                "price": Decimal("199.99"),
                "images": ["/media/products/pendant-light.jpg", "/media/products/pendant-light-detail.jpg"],
                "stock_quantity": 30,
                "is_featured": True,
                "category": lighting_category,
                "sku_prefix": "LIGHT"
            },
            {
                "name": "Designer Floor Lamp",
                "description": "Architectural floor lamp with brass finish and marble base. Statement piece for any room.",
                "price": Decimal("299.99"),
                "images": ["/media/products/floor-lamp.jpg", "/media/products/floor-lamp-detail.jpg"],
                "stock_quantity": 15,
                "is_featured": False,
                "category": lighting_category,
                "sku_prefix": "LIGHT"
            },
            # Storage
            {
                "name": "Modern TV Console",
                "description": "Sleek TV console with cable management and storage drawers. Perfect for modern living rooms.",
                "price": Decimal("699.99"),
                "images": ["/media/products/tv-console.jpg", "/media/products/tv-console-detail.jpg"],
                "stock_quantity": 20,
                "is_featured": True,
                "category": storage_category,
                "sku_prefix": "STORE"
            },
            {
                "name": "Minimalist Bookshelf",
                "description": "Contemporary bookshelf with metal frame and wooden shelves. Industrial-modern design.",
                "price": Decimal("449.99"),
                "images": ["/media/products/bookshelf.jpg", "/media/products/bookshelf-detail.jpg"],
                "stock_quantity": 25,
                "is_featured": False,
                "category": storage_category,
                "sku_prefix": "STORE"
            },
            # Home Decor
            {
                "name": "Luxury Velvet Cushion",
                "description": "Soft velvet cushion with gold piping. Available in multiple colors.",
                "price": Decimal("49.99"),
                "images": ["/media/products/velvet-cushion.jpg", "/media/products/velvet-cushion-detail.jpg"],
                "stock_quantity": 100,
                "is_featured": True,
                "category": decor_category,
                "sku_prefix": "DECOR"
            },
            {
                "name": "Abstract Wall Art",
                "description": "Contemporary abstract canvas print. Perfect for modern interiors.",
                "price": Decimal("199.99"),
                "images": ["/media/products/wall-art.jpg", "/media/products/wall-art-detail.jpg"],
                "stock_quantity": 30,
                "is_featured": False,
                "category": decor_category,
                "sku_prefix": "DECOR"
            },
            # Additional Chairs
            {
                "name": "Velvet Dining Chair Set",
                "description": "Set of 2 luxurious velvet dining chairs with gold-finished legs.",
                "price": Decimal("399.99"),
                "images": ["/media/products/velvet-dining-chair.jpg", "/media/products/velvet-dining-chair-detail.jpg"],
                "stock_quantity": 40,
                "is_featured": True,
                "category": dining_chairs_category,
                "sku_prefix": "DCHAIR"
            },
            {
                "name": "Rattan Accent Chair",
                "description": "Natural rattan accent chair with cushion. Perfect for boho-inspired spaces.",
                "price": Decimal("299.99"),
                "images": ["/media/products/rattan-chair.jpg", "/media/products/rattan-chair-detail.jpg"],
                "stock_quantity": 25,
                "is_featured": False,
                "category": chairs_category,
                "sku_prefix": "CHAIR"
            },
            # Additional Storage
            {
                "name": "Floating Wall Shelf Set",
                "description": "Set of 3 floating shelves in various sizes. Modern and minimal design.",
                "price": Decimal("129.99"),
                "images": ["/media/products/floating-shelves.jpg", "/media/products/floating-shelves-detail.jpg"],
                "stock_quantity": 50,
                "is_featured": True,
                "category": storage_category,
                "sku_prefix": "STORE"
            },
            {
                "name": "Storage Ottoman",
                "description": "Multifunctional ottoman with hidden storage space. Perfect for small spaces.",
                "price": Decimal("199.99"),
                "images": ["/media/products/storage-ottoman.jpg", "/media/products/storage-ottoman-detail.jpg"],
                "stock_quantity": 35,
                "is_featured": False,
                "category": storage_category,
                "sku_prefix": "STORE"
            },
            # Additional Lighting
            {
                "name": "Geometric Table Lamp",
                "description": "Modern geometric table lamp with brass finish and white shade.",
                "price": Decimal("159.99"),
                "images": ["/media/products/table-lamp.jpg", "/media/products/table-lamp-detail.jpg"],
                "stock_quantity": 40,
                "is_featured": True,
                "category": lighting_category,
                "sku_prefix": "LIGHT"
            },
            {
                "name": "LED Wall Sconce",
                "description": "Contemporary LED wall sconce with adjustable head. Perfect for bedside lighting.",
                "price": Decimal("129.99"),
                "images": ["/media/products/wall-sconce.jpg", "/media/products/wall-sconce-detail.jpg"],
                "stock_quantity": 45,
                "is_featured": False,
                "category": lighting_category,
                "sku_prefix": "LIGHT"
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
                    "base_price": product_data["price"],
                    "category": product_data["category"],
                    "images": product_data["images"],
                    "stock_quantity": product_data["stock_quantity"],
                    "slug": slugify(name),
                    "is_featured": product_data["is_featured"],
                    "sku": self.generate_sku(name, product_data["sku_prefix"]),
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