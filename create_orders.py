import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avantlush_backend.settings')
django.setup()

from avantlush_backend.api.models import CustomUser, Order, OrderItem, Product, OrderTracking
from django.utils import timezone
import random
from decimal import Decimal

# User email
email = 'danieludechukwu117@gmail.com'
count = 5

try:
    user = CustomUser.objects.get(email=email)
    print(f"Found user: {user.email}")
except CustomUser.DoesNotExist:
    print("User not found. Please check the email address.")
    sys.exit(1)

# Use specific products by name
product_names = [
    "Ergonomic Chair",
    "LED Wall Sconce",
    "Three Seater",
    "Executive Office Chair",
    "Rattan Accent Chair",
    "Velvet Dining Chair Set"
]

products = list(Product.objects.filter(name__in=product_names))

if not products:
    print("No products found with the specified names. Using all available products...")
    products = list(Product.objects.all()[:10])
    
    if not products:
        print("No products found in the database. Please add some products first.")
        sys.exit(1)

print(f"Found {len(products)} products to use in orders")

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
    
    # Add tracking events based on status
    if status in ['PROCESSING', 'SHIPPED', 'DELIVERED']:
        OrderTracking.objects.create(
            order=order,
            status="Order Confirmed",
            location="AvantLush Warehouse",
            description="Your order has been confirmed and is being processed.",
            timestamp=timezone.now() - timezone.timedelta(days=5)
        )
    
    if status in ['SHIPPED', 'DELIVERED']:
        OrderTracking.objects.create(
            order=order,
            status="Order Shipped",
            location="Lagos Distribution Center",
            description="Your order has been shipped and is on its way to you.",
            timestamp=timezone.now() - timezone.timedelta(days=2)
        )
    
    if status == 'DELIVERED':
        OrderTracking.objects.create(
            order=order,
            status="Order Delivered",
            location="Customer Address",
            description="Your order has been delivered successfully.",
            timestamp=timezone.now() - timezone.timedelta(hours=12)
        )
    
    print(f"Created order #{order.order_number} with status {status} and {num_products} products. Total: ${order.total}")

print(f"Done! Created {count} dummy orders.")
