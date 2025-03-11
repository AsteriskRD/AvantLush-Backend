from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def notify_order_update(order_id, status):
    """Send email notification for order status updates"""
    from .models import Order  # Import here to avoid circular import
    
    try:
        order = Order.objects.get(id=order_id)
        subject = f'Order #{order.id} Status Update'
        message = f'Your order #{order.id} has been updated to: {status}'
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            fail_silently=False,
        )
    except Order.DoesNotExist:
        pass

@shared_task
def notify_ticket_update(ticket_id, update_type):
    """Send email notification for ticket updates"""
    from .models import SupportTicket
    
    try:
        ticket = SupportTicket.objects.get(id=ticket_id)
        subject = f'Support Ticket #{ticket.id} Update'
        message = f'Your support ticket has been updated. Status: {ticket.status}'
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [ticket.user.email],
            fail_silently=False,
        )
    except SupportTicket.DoesNotExist:
        pass

@shared_task
def check_wishlist_stock():
    """Check stock status for wishlist items and notify users"""
    from .models import WishlistItem, WishlistNotification
    
    wishlist_items = WishlistItem.objects.select_related('product', 'wishlist__user')
    
    for item in wishlist_items:
        if item.product.stock_quantity > 0:
            # Create notification
            WishlistNotification.objects.create(
                wishlist_item=item,
                notification_type='STOCK_AVAILABLE',
                message=f'{item.product.name} is now back in stock!'
            )
            
            # Send email
            send_mail(
                'Wishlist Item Back in Stock',
                f'{item.product.name} is now available!',
                settings.DEFAULT_FROM_EMAIL,
                [item.wishlist.user.email],
                fail_silently=False,
            )
@shared_task
def send_cart_abandonment_reminder():
    """Send reminders for abandoned carts after X hours"""
    from .models import Cart
    from django.utils import timezone
    
    # Get carts that haven't been updated in 24 hours
    abandoned_time = timezone.now() - timezone.timedelta(hours=24)
    abandoned_carts = Cart.objects.filter(
        updated_at__lt=abandoned_time,
        items__isnull=False
    ).select_related('user')
    
    for cart in abandoned_carts:
        send_mail(
            'Items waiting in your cart',
            'Don\'t forget about the items in your cart!',
            settings.DEFAULT_FROM_EMAIL,
            [cart.user.email],
            fail_silently=False,
        )

@shared_task
def sync_shipping_status(order_id):
    """Sync shipping status with carrier's API"""
    from .models import Order, OrderTracking
    
    try:
        order = Order.objects.get(id=order_id)
        # Add logic to fetch shipping status from carrier API
        # Update order tracking information
        OrderTracking.objects.create(
            order=order,
            status='NEW_STATUS',
            location='LOCATION',
            description='Status update from carrier'
        )
    except Order.DoesNotExist:
        pass

@shared_task
def send_review_reminder():
    """Send review reminders for delivered orders"""
    from .models import Order, Review
    from django.utils import timezone
    
    # Get orders delivered in last 7 days without reviews
    delivery_date = timezone.now() - timezone.timedelta(days=7)
    delivered_orders = Order.objects.filter(
        status='DELIVERED',
        updated_at__gte=delivery_date
    ).exclude(
        items__product__reviews__user=F('user')
    ).select_related('user')
    
    for order in delivered_orders:
        send_mail(
            'Share your experience',
            'How was your recent purchase? Leave a review!',
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            fail_silently=False,
        )

@shared_task
def cleanup_expired_data():
    """Clean up expired tokens and unused data"""
    from .models import EmailVerificationToken, PasswordResetToken
    from django.utils import timezone
    
    # Clean up expired tokens
    EmailVerificationToken.objects.filter(
        expires_at__lt=timezone.now(),
        is_used=False
    ).delete()
    
    PasswordResetToken.objects.filter(
        expires_at__lt=timezone.now(),
        is_used=False
    ).delete()


@shared_task
def monitor_failed_orders():
    """Monitor and report failed orders"""
    from .models import Order
    from django.core.mail import mail_admins
    
    failed_orders = Order.objects.filter(
        payment_status='FAILED',
        created_at__gte=timezone.now() - timezone.timedelta(hours=24)
    )
    
    if failed_orders.exists():
        message = f"Failed orders in last 24 hours: {failed_orders.count()}"
        mail_admins(
            'Failed Orders Alert',
            message,
            fail_silently=False
        )