from django.core.management.base import BaseCommand
from django.utils import timezone
from avantlush_backend.api.models import CustomUser, Order, OrderItem, Product, OrderTracking
import random
from decimal import Decimal
from datetime import timedelta

class Command(BaseCommand):
    help = 'Creates dummy orders for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, default='danieludechukwu117@gmail.com',
                            help='Email of the user to create orders for')
        parser.add_argument('--count', type=int, default=5,
                            help='Number of orders to create')

    def handle(self, *args, **options):
        email = options['email']
        count = options['count']

        self.stdout.write(self.style.SUCCESS(f'Creating {count} orders for {email}'))

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

        # Create orders with different statuses
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
            
            # Create the order with exact text matching what's shown in console
            order = Order(
                user=user,
                status=status,
                payment_type='CREDIT',
                payment_status='PAID',
                order_type='STANDARD',
                shipping_address=f"{random.randint(1, 999)} Main St",
                shipping_city="Lagos",
                shipping_state="Lagos",
                shipping_country="Nigeria",
                shipping_zip="100001",
                subtotal=Decimal('0.00'),
                shipping_cost=Decimal('9.99'),
                tax=Decimal('5.99'),
                discount=Decimal('0.00'),
                total=Decimal('0.00'),
                billing_address=f"{random.randint(1, 999)} Main St, Lagos, Nigeria",
                # Use this exact note text to match what's shown in your console
                note="A demo order created for testing purposes."
            )
            
            # Save to generate order number
            order.save()
            
            # Add products as order items - keeping this simple to match structure
            num_products = min(random.randint(1, 3), len(products))
            order_products = random.sample(products, num_products)
            
            # Track subtotal for order
            order_subtotal = Decimal('0.00')
            
            for product in order_products:
                quantity = random.randint(1, 3)
                price = product.base_price  # Use base_price from product
                
                # Create order item
                item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    # Use price field (will show as unit_price in serializer)
                    price=Decimal(str(price)),
                    # Use subtotal field (will show as total_price in serializer)
                    subtotal=Decimal(str(price)) * quantity
                )
                
                order_subtotal += item.subtotal
            
            # Recalculate order total
            order.subtotal = order_subtotal
            order.total = order.subtotal + order.shipping_cost + order.tax - order.discount
            order.save()
            
            # Calculate estimated delivery date based on order type
            if order.order_type == 'STANDARD':
                delivery_days = random.randint(3, 5)
            else:  # EXPRESS
                delivery_days = random.randint(1, 2)
                
            estimated_delivery_date = timezone.now() + timedelta(days=delivery_days)
            
            # Add tracking events based on status
            if status in ['PROCESSING', 'SHIPPED', 'DELIVERED']:
                OrderTracking.objects.create(
                    order=order,
                    status="Order Confirmed",
                    location="AvantLush Warehouse",
                    description="Your order has been confirmed and is being processed.",
                    timestamp=timezone.now() - timedelta(days=5)
                )
                
                # Add estimated delivery information - formatted exactly as expected by serializer
                OrderTracking.objects.create(
                    order=order,
                    status="Estimated Delivery",
                    location="AvantLush Logistics",
                    description=f"Your order is expected to be delivered by {estimated_delivery_date.strftime('%A, %B %d, %Y')}.",
                    timestamp=timezone.now() - timedelta(days=4)
                )
            
            if status in ['SHIPPED', 'DELIVERED']:
                OrderTracking.objects.create(
                    order=order,
                    status="Order Shipped",
                    location="Lagos Distribution Center",
                    description="Your order has been shipped and is on its way to you.",
                    timestamp=timezone.now() - timedelta(days=2)
                )
            
            if status == 'DELIVERED':
                # For delivered orders, use a past date as the actual delivery date
                actual_delivery_date = timezone.now() - timedelta(hours=12)
                OrderTracking.objects.create(
                    order=order,
                    status="Order Delivered",
                    location="Customer Address",
                    description=f"Your order has been delivered successfully on {actual_delivery_date.strftime('%A, %B %d, %Y at %I:%M %p')}.",
                    timestamp=actual_delivery_date
                )
            
            self.stdout.write(self.style.SUCCESS(
                f"Created order #{order.order_number} with status {status} and {num_products} products. "
                f"Total: ${order.total}. Estimated delivery: {estimated_delivery_date.strftime('%Y-%m-%d')}"
            ))

        self.stdout.write(self.style.SUCCESS(f"Done! Created {count} dummy orders."))