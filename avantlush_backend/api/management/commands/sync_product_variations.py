from django.core.management.base import BaseCommand
from django.utils import timezone
from avantlush_backend.api.models import (
    CustomUser, Order, OrderItem, Product, OrderTracking,
    Size, ProductSize, Color, ProductColor
)
import random
from decimal import Decimal
from datetime import timedelta

class Command(BaseCommand):
    help = 'Synchronize product variations with their sizes and colors'

    def handle(self, *args, **options):
        products = Product.objects.all()
        total = products.count()
        
        self.stdout.write(f"Syncing variations for {total} products...")
        
        for i, product in enumerate(products):
            # Call the sync methods
            self.sync_available_sizes(product)
            self.sync_available_colors(product)
            
            # Print progress
            if (i + 1) % 10 == 0 or (i + 1) == total:
                self.stdout.write(f"Processed {i + 1}/{total} products")
        
        self.stdout.write(self.style.SUCCESS('Successfully synchronized all product variations!'))
    
    def sync_available_sizes(self, product):
        """Synchronize available sizes for the product based on its variations"""
        # Get all sizes from variations
        variation_sizes = set()
        for variation in product.variations.all():
            # Add sizes from ManyToMany relationship
            variation_sizes.update(size.id for size in variation.sizes.all())
            # Add size from ForeignKey relationship if exists
            if variation.size:
                variation_sizes.add(variation.size.id)
        
        # Clear existing product sizes
        ProductSize.objects.filter(product=product).delete()
        
        # Create new product sizes
        for size_id in variation_sizes:
            try:
                size = Size.objects.get(id=size_id)
                ProductSize.objects.create(product=product, size=size)
            except Size.DoesNotExist:
                pass
    
    def sync_available_colors(self, product):
        """Synchronize available colors for the product based on its variations"""
        # Get all colors from variations
        variation_colors = set()
        for variation in product.variations.all():
            # Add colors from ManyToMany relationship
            variation_colors.update(color.id for color in variation.colors.all())
            # Add color from ForeignKey relationship if exists
            if variation.color:
                variation_colors.add(variation.color.id)
        
        # Clear existing product colors
        ProductColor.objects.filter(product=product).delete()
        
        # Create new product colors
        for color_id in variation_colors:
            try:
                color = Color.objects.get(id=color_id)
                ProductColor.objects.create(product=product, color=color)
            except Color.DoesNotExist:
                pass