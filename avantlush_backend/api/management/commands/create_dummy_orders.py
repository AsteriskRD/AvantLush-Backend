from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
import random
from datetime import timedelta

# Import your models with the correct path
from avantlush_backend.api.models import Order, OrderItem, OrderTracking, Customer, Product

class Command(BaseCommand):
    help = 'Creates dummy order data with Pending, Shipped, and Delivered statuses'

    def add_arguments(self, parser):
        # Optional argument to specify if existing orders should be cleared
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing orders before creating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing orders...')
            Order.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Orders cleared!'))

        # Get or create a user for the orders - FIXED: using email instead of username
        User = get_user_model()
        user, created = User.objects.get_or_create(
            email='dummy@example.com',
            defaults={
                'first_name': 'Dummy',
                'last_name': 'User'
            }
        )
        
        # Get or create a customer
        customer, created = Customer.objects.get_or_create(
            user=user,
            defaults={
                'name': 'Dummy Customer',
                'email': 'dummy@example.com',
                'phone': '123-456-7890'
                # Note: Customer model doesn't have address fields in your model definition
            }
        )
        
        # Get some products (or create if none exist)
        products = list(Product.objects.all())
        if not products:
            # Create sample products if none exist
            self.stdout.write('No products found. Creating dummy products...')
            for i in range(1, 6):
                product = Product.objects.create(
                    name=f'Product {i}',
                    price=Decimal(str(random.uniform(10.0, 100.0))).quantize(Decimal('0.01')),
                    # Add other required fields for your Product model
                )
                products.append(product)
        
        # Order statuses to create
        statuses = ['PENDING', 'SHIPPED', 'DELIVERED']
        
        # Create one order for each status
        for status in statuses:
            # Create base order
            order = Order.objects.create(
                user=user,
                customer=customer,
                status=status,
                payment_type=random.choice(['CASH', 'CREDIT', 'DEBIT', 'TRANSFER']),
                payment_status='PAID' if status != 'PENDING' else 'PENDING',
                order_type=random.choice(['STANDARD', 'EXPRESS', 'PICKUP']),
                shipping_address='456 Shipping St',
                shipping_city='Shipping City',
                shipping_state='CA',
                shipping_country='USA',
                shipping_zip='54321',
                billing_address='123 Billing St, Billing City, CA, USA',
                subtotal=Decimal('0.00'),  # Will be calculated by OrderItems
                shipping_cost=Decimal('10.00'),
                tax=Decimal('5.00'),
                discount=Decimal('2.00'),
            )
            
            # Add order items (between 1 and 3 items)
            for _ in range(random.randint(1, 3)):
                product = random.choice(products)
                quantity = random.randint(1, 5)
                price = product.price
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price,
                    subtotal=price * quantity
                )
            
            # Create tracking entries based on status
            if status == 'PENDING':
                OrderTracking.objects.create(
                    order=order,
                    status='Order Received',
                    location='Processing Center',
                    description='Your order has been received and is being processed.'
                )
            elif status == 'SHIPPED':
                # Create multiple tracking entries for shipped order
                OrderTracking.objects.create(
                    order=order,
                    status='Order Received',
                    location='Processing Center',
                    description='Your order has been received and is being processed.',
                    timestamp=timezone.now() - timedelta(days=2)
                )
                OrderTracking.objects.create(
                    order=order,
                    status='Order Processed',
                    location='Processing Center',
                    description='Your order has been processed and is being prepared for shipping.',
                    timestamp=timezone.now() - timedelta(days=1)
                )
                OrderTracking.objects.create(
                    order=order,
                    status='Order Shipped',
                    location='Distribution Center',
                    description='Your order has been shipped and is on its way to you.'
                )
            elif status == 'DELIVERED':
                # Create full tracking history for delivered order
                OrderTracking.objects.create(
                    order=order,
                    status='Order Received',
                    location='Processing Center',
                    description='Your order has been received and is being processed.',
                    timestamp=timezone.now() - timedelta(days=3)
                )
                OrderTracking.objects.create(
                    order=order,
                    status='Order Processed',
                    location='Processing Center',
                    description='Your order has been processed and is being prepared for shipping.',
                    timestamp=timezone.now() - timedelta(days=2)
                )
                OrderTracking.objects.create(
                    order=order,
                    status='Order Shipped',
                    location='Distribution Center',
                    description='Your order has been shipped and is on its way to you.',
                    timestamp=timezone.now() - timedelta(days=1, hours=12)
                )
                OrderTracking.objects.create(
                    order=order,
                    status='Out for Delivery',
                    location='Local Courier',
                    description='Your order is out for delivery and will arrive today.',
                    timestamp=timezone.now() - timedelta(hours=6)
                )
                OrderTracking.objects.create(
                    order=order,
                    status='Delivered',
                    location='Customer Address',
                    description='Your order has been delivered. Thank you for shopping with us!',
                    timestamp=timezone.now() - timedelta(hours=2)
                )
            
            self.stdout.write(self.style.SUCCESS(f'Created {status} order: {order.order_number}'))
            
        self.stdout.write(self.style.SUCCESS('Successfully created dummy orders!'))