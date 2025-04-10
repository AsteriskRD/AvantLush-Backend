from django.core.management.base import BaseCommand
from django.utils import timezone
from avantlush_backend.api.models import CustomUser, Order, OrderItem, Product, OrderTracking
import random
from decimal import Decimal
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
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

        # Use specific products by name
        product_names = [
            "Ergonomic Chair",
            "LED Wall Sconce",
            "Three Seater",
            "Executive Office Chair",
            "Rattan Accent Chair",
            "Velvet Dining Chair Set"
        ]

        # Image URLs for products
        PRODUCT_IMAGES = {
            "Ergonomic Chair": {
                "main_image": "https://res.cloudinary.com/dvfwa8fzh/image/upload/v1738680206/products/Egonomic_chair2_pycpbr.jpg",
                "images": [
                    "https://res.cloudinary.com/dvfwa8fzh/image/upload/v1738680192/products/Chair_lno7it.jpg",
                    "https://res.cloudinary.com/dvfwa8fzh/image/upload/v1738680221/products/single_chair_rk11hk.jpg"
                ]
            },
            "LED Wall Sconce": {
                "main_image": "https://res.cloudinary.com/dvfwa8fzh/image/upload/v1738680218/products/lampstand_hyrikx.jpg",
                "images": [
                    "https://res.cloudinary.com/dvfwa8fzh/image/upload/v1738680209/products/flowervase_uqrdfc.jpg"
                ]
            },
            "Three Seater": {
                "main_image": "https://res.cloudinary.com/dvfwa8fzh/image/upload/v1738680226/products/three_seater_w3145s.jpg",
                "images": [
                    "https://res.cloudinary.com/dvfwa8fzh/image/upload/v1738680240/products/WhatsApp_Image_2025-02-04_at_12.48.24_3218da74_gtuxwe.jpg"
                ]
            },
            "Executive Office Chair": {
                "main_image": "https://res.cloudinary.com/dvfwa8fzh/image/upload/v1738680192/products/Chair_lno7it.jpg",
                "images": [
                    "https://res.cloudinary.com/dvfwa8fzh/image/upload/v1738680206/products/Egonomic_chair2_pycpbr.jpg"
                ]
            },
            "Rattan Accent Chair": {
                "main_image": "https://res.cloudinary.com/dvfwa8fzh/image/upload/v1738680221/products/single_chair_rk11hk.jpg",
                "images": [
                    "https://res.cloudinary.com/dvfwa8fzh/image/upload/v1738680192/products/Chair_lno7it.jpg"
                ]
            },
            "Velvet Dining Chair Set": {
                "main_image": "https://res.cloudinary.com/dvfwa8fzh/image/upload/v1738680195/products/Dinng_table2_vyc9al.jpg",
                "images": [
                    "https://res.cloudinary.com/dvfwa8fzh/image/upload/v1738680197/products/dinng_table4_cnyuyz.jpg",
                    "https://res.cloudinary.com/dvfwa8fzh/image/upload/v1738680200/products/dinnig_table_nak9zd.jpg",
                    "https://res.cloudinary.com/dvfwa8fzh/image/upload/v1738680203/products/dinnig_table2_hkaehc.jpg"
                ]
            }
        }

        products = list(Product.objects.filter(name__in=product_names))

        if not products:
            self.stdout.write(self.style.WARNING("No products found with the specified names. Using all available products..."))
            products = list(Product.objects.all()[:10])
            
            if not products:
                self.stdout.write(self.style.ERROR("No products found in the database. Please add some products first."))
                return

        # Update products with images
        for product in products:
            if product.name in PRODUCT_IMAGES:
                # Update main image
                try:
                    # For CloudinaryField, we need to set the URL properly
                    # This approach assumes the URL is already in Cloudinary
                    main_image_url = PRODUCT_IMAGES[product.name]["main_image"]
                    
                    # Extract the public_id from the URL (everything after the last slash and before the file extension)
                    public_id = main_image_url.split('/')[-1].split('.')[0]
                    
                    # Set the main_image field with the public_id
                    product.main_image = main_image_url
                    
                    # Update images JSONField
                    product.images = PRODUCT_IMAGES[product.name]["images"]
                    
                    product.save()
                    self.stdout.write(self.style.SUCCESS(f"Updated images for {product.name}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error updating images for {product.name}: {str(e)}"))

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
            
            # Create the order
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
                note="This is a dummy order created for testing purposes."
            )
            
            # Save to generate order number
            order.save()
            
            # Add products as order items
            num_products = min(random.randint(1, 3), len(products))
            order_products = random.sample(products, num_products)
            
            for product in order_products:
                quantity = random.randint(1, 3)
                price = product.price
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price,
                    subtotal=price * quantity
                )
            
            # Recalculate order total
            order.subtotal = sum(item.subtotal for item in order.items.all())
            order.total = order.subtotal + order.shipping_cost + order.tax - order.discount
            order.save()
            
            # Calculate estimated delivery date based on order type
            # Standard: 3-5 days, Express: 1-2 days
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
                
                # Add estimated delivery information
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
