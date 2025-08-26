from django.core.management.base import BaseCommand
from django.utils import timezone
from avantlush_backend.api.models import CustomUser, Order, OrderItem, Product, OrderTracking, Payment
import random
from decimal import Decimal
from datetime import timedelta

class Command(BaseCommand):
    help = 'Creates flat order items for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, default='danieludechukwu117@gmail.com',
                            help='Email of the user to create orders for')
        parser.add_argument('--count', type=int, default=5,
                            help='Number of order items to create')

    def handle(self, *args, **options):
        email = options['email']
        count = options['count']

        self.stdout.write(self.style.SUCCESS(f'Creating {count} order items for {email}'))

        try:
            user = CustomUser.objects.get(email=email)
            self.stdout.write(self.style.SUCCESS(f"Found user: {user.email}"))
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR("User not found. Please check the email address."))
            return

        # Use specific products by name - make sure these exist in your database
        product_names = [
            "Rattan Accent Chair",
            "LED Wall Sconce",
            "Executive Office Chair",
            "Geometric Table Lamp",
            "Storage Ottoman",
            "Floating Wall Shelf Set"
        ]

        products = list(Product.objects.filter(name__in=product_names))

        if not products:
            self.stdout.write(self.style.WARNING("No products found with the specified names. Using all available products..."))
            products = list(Product.objects.all()[:10])
            
            if not products:
                self.stdout.write(self.style.ERROR("No products found in the database. Please add some products first."))
                return

        self.stdout.write(self.style.SUCCESS(f"Found {len(products)} products to use in orders"))

        # Create a master "All Orders" container if needed
        # Note: This is conceptual - you may need to adjust based on your actual model structure
        current_date = timezone.now().strftime('%Y%m%d')
        master_order_number = f"ORD-{current_date}-0000"
        
        try:
            master_order = Order.objects.get(order_number=master_order_number)
        except Order.DoesNotExist:
            master_order = Order.objects.create(
                user=user,
                order_number=master_order_number,
                status='PROCESSING',
                payment_type='MULTIPLE',
                payment_status='MIXED',
                order_type='STANDARD',
                shipping_address="Multiple addresses",
                total=Decimal('0.00'),
                note="Master order container"
            )

        # Create individual order items
        for i in range(count):
            # Select a status based on index
            if i < 2:
                status = 'DELIVERED'
            elif i < 3:
                status = 'SHIPPED'
            elif i < 4:
                status = 'PROCESSING'
            else:
                status = 'PENDING'
            
            # Pick a random product
            product = random.choice(products)
            quantity = random.randint(1, 3)
            unit_price = product.price if hasattr(product, 'price') else Decimal('99.99')
            total_price = unit_price * quantity
            
            # Create a unique identifier for this item
            item_id = OrderItem.objects.count() + 1
            item_number = f"ITEM-{current_date}-{item_id:04d}"
            
            # Create the order item directly
            item = OrderItem.objects.create(
                order=master_order,  # All items belong to the master order
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                status=status,  # Add status field to OrderItem if needed
                item_number=item_number  # Add item_number field to OrderItem if needed
            )
            
            # Calculate estimated delivery date
            delivery_days = random.randint(1, 5)
            estimated_delivery_date = timezone.now() + timedelta(days=delivery_days)
            
            # Add tracking specifically for this item if your model supports it
            # You may need to modify your OrderTracking model to link to OrderItem instead of Order
            if hasattr(OrderTracking, 'order_item'):
                if status in ['PROCESSING', 'SHIPPED', 'DELIVERED']:
                    OrderTracking.objects.create(
                        order_item=item,
                        status="Item Processing",
                        location="AvantLush Warehouse",
                        description="Your item is being processed.",
                        timestamp=timezone.now() - timedelta(days=3)
                    )
                
                    OrderTracking.objects.create(
                        order_item=item,
                        status="Estimated Delivery",
                        location="AvantLush Logistics",
                        description=f"This item is expected to be delivered by {estimated_delivery_date.strftime('%A, %B %d, %Y')}.",
                        timestamp=timezone.now() - timedelta(days=2)
                    )
                
                if status in ['SHIPPED', 'DELIVERED']:
                    OrderTracking.objects.create(
                        order_item=item,
                        status="Item Shipped",
                        location="Distribution Center",
                        description="Your item has been shipped.",
                        timestamp=timezone.now() - timedelta(days=1)
                    )
                
                if status == 'DELIVERED':
                    actual_delivery_date = timezone.now() - timedelta(hours=random.randint(1, 24))
                    OrderTracking.objects.create(
                        order_item=item,
                        status="Item Delivered",
                        location="Customer Address",
                        description=f"Your item has been delivered on {actual_delivery_date.strftime('%A, %B %d, %Y at %I:%M %p')}.",
                        timestamp=actual_delivery_date
                    )
            
            self.stdout.write(self.style.SUCCESS(
                f"Created order item #{item_number} with status {status} for product {product.name} (qty: {quantity}). "
                f"Total: ${total_price}. Estimated delivery: {estimated_delivery_date.strftime('%Y-%m-%d')}"
            ))

        self.stdout.write(self.style.SUCCESS(f"Done! Created {count} order items."))