from django.core.management.base import BaseCommand
from avantlush_backend.api.models import Product, ProductVariation
from avantlush_backend.api.utils import generate_sku


class Command(BaseCommand):
    help = 'Regenerate SKUs for all products and product variations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--products-only',
            action='store_true',
            help='Only regenerate SKUs for products, not variations',
        )
        parser.add_argument(
            '--variations-only',
            action='store_true',
            help='Only regenerate SKUs for product variations, not products',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration even if SKU already exists',
        )

    def handle(self, *args, **options):
        products_only = options['products_only']
        variations_only = options['variations_only']
        force = options['force']

        if not products_only and not variations_only:
            # Regenerate both products and variations
            self.regenerate_product_skus(force)
            self.regenerate_variation_skus(force)
        elif products_only:
            self.regenerate_product_skus(force)
        elif variations_only:
            self.regenerate_variation_skus(force)

    def regenerate_product_skus(self, force=False):
        """Regenerate SKUs for all products"""
        self.stdout.write("🔄 Regenerating SKUs for products...")
        
        if force:
            products = Product.objects.all()
        else:
            products = Product.objects.filter(sku__isnull=True) | Product.objects.filter(sku='')
        
        updated_count = 0
        for product in products:
            try:
                old_sku = product.sku
                product.sku = generate_sku(product.name, product.category, product.sku)
                product.save(update_fields=['sku'])
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Product '{product.name}': {old_sku} → {product.sku}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error updating product '{product.name}': {e}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"🎉 Successfully updated SKUs for {updated_count} products")
        )

    def regenerate_variation_skus(self, force=False):
        """Regenerate SKUs for all product variations"""
        self.stdout.write("🔄 Regenerating SKUs for product variations...")
        
        if force:
            variations = ProductVariation.objects.all()
        else:
            variations = ProductVariation.objects.filter(sku__isnull=True) | ProductVariation.objects.filter(sku='')
        
        updated_count = 0
        for variation in variations:
            try:
                old_sku = variation.sku
                variation.sku = variation.generate_sku()
                variation.save(update_fields=['sku'])
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Variation '{variation}': {old_sku} → {variation.sku}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error updating variation '{variation}': {e}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"🎉 Successfully updated SKUs for {updated_count} variations")
        )
