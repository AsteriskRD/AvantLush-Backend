from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile, Customer

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            full_name=instance.get_full_name() or instance.email
        )

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    Profile.objects.get_or_create(
        user=instance,
        defaults={'full_name': instance.get_full_name() or instance.email}
    )


# --- Customer synchronization ---
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_customer_for_user(sender, instance, created, **kwargs):
    """Ensure there is a Customer row for every CustomUser.

    - On first creation, create or link a `Customer` with the same email.
    - On subsequent saves, keep the `Customer.name` in sync if empty or clearly different.
    """
    # Try to find an existing customer linked to this user
    customer = Customer.objects.filter(user=instance).first()

    # If none linked, try by email
    if customer is None:
        customer = Customer.objects.filter(email__iexact=instance.email).first()
        if customer is not None and customer.user is None:
            customer.user = instance
            customer.save()

    # If still none, create it
    if customer is None:
        # Try to get a proper name from the user
        if instance.first_name and instance.last_name:
            display_name = f"{instance.first_name} {instance.last_name}".strip()
        elif instance.first_name:
            display_name = instance.first_name.strip()
        elif instance.last_name:
            display_name = instance.last_name.strip()
        else:
            # Fallback: use email prefix as name (remove @domain.com)
            email_prefix = instance.email.split('@')[0]
            # Capitalize first letter and replace dots/underscores with spaces
            display_name = email_prefix.replace('.', ' ').replace('_', ' ').title()
        
        Customer.objects.create(
            user=instance,
            name=display_name,
            email=instance.email,
        )
        return

    # Keep name up to date if the customer has a placeholder name and user now has a better one
    if customer:
        # Try to get a proper name from the user
        if instance.first_name and instance.last_name:
            preferred_name = f"{instance.first_name} {instance.last_name}".strip()
        elif instance.first_name:
            preferred_name = instance.first_name.strip()
        elif instance.last_name:
            preferred_name = instance.last_name.strip()
        else:
            # Fallback: use email prefix as name
            email_prefix = instance.email.split('@')[0]
            preferred_name = email_prefix.replace('.', ' ').replace('_', ' ').title()
        
        # Update if the name is different and better than current
        if preferred_name and customer.name != preferred_name:
            # Only update if the new name is more descriptive than the current one
            current_is_email = '@' in customer.name
            new_is_email = '@' in preferred_name
            
            if not current_is_email or (current_is_email and not new_is_email):
                customer.name = preferred_name
                customer.save(update_fields=["name"])

# --- NEW: Sync from Customer back to CustomUser ---
@receiver(post_save, sender=Customer)
def sync_customer_to_user(sender, instance, created, **kwargs):
    """Sync Customer changes back to the linked CustomUser.
    
    This ensures that when you update customer details in your custom dashboard,
    the changes are reflected in Django Admin as well.
    """
    if not instance.user:  # Skip if no linked user
        return
    
    user = instance.user
    updated = False
    
    # Sync name changes
    if instance.name and instance.name != user.get_full_name():
        # Parse the customer name into first_name and last_name
        name_parts = instance.name.strip().split(' ', 1)
        if len(name_parts) == 1:
            # Single name - put it in first_name
            if user.first_name != name_parts[0]:
                user.first_name = name_parts[0]
                user.last_name = ''
                updated = True
        else:
            # Multiple names - first part is first_name, rest is last_name
            first_name, last_name = name_parts
            if user.first_name != first_name or user.last_name != last_name:
                user.first_name = first_name
                user.last_name = last_name
                updated = True
    
    # Sync email changes (if email was changed in customer)
    if instance.email != user.email:
        user.email = instance.email
        updated = True
    
    # Sync status changes (affects user.is_active)
    if instance.status == 'active' and not user.is_active:
        user.is_active = True
        updated = True
    elif instance.status == 'blocked' and user.is_active:
        user.is_active = False
        updated = True
    
    # Sync photo changes (customer photo becomes profile photo)
    # REMOVED: Customer model no longer has photo field
    # if hasattr(instance, 'photo') and instance.photo:
    #     try:
    #         profile = user.profile
    #         if profile.photo != instance.photo:
    #             profile.photo = instance.photo
    #             profile.save(update_fields=['photo'])
    #             print(f"Customer sync: Updated profile {profile.id} photo to match customer photo")
    #     except Profile.DoesNotExist:
    #         pass  # Profile doesn't exist yet
    
    # Also sync the other way - if user.is_active changed, update customer.status
    if user.is_active and instance.status != 'active':
        instance.status = 'active'
        # Don't save here to avoid infinite loop - just mark as updated
        updated = True
    elif not user.is_active and instance.status != 'blocked':
        instance.status = 'blocked'
        # Don't save here to avoid infinite loop - just mark as updated
        updated = True
    
            # Save user if any changes were made
    if updated:
        user.save(update_fields=['first_name', 'last_name', 'email', 'is_active'])
        print(f"Synced customer {instance.id} changes to user {user.id}")

# --- NEW: Sync from Profile to Customer ---
@receiver(post_save, sender=Profile)
def sync_profile_to_customer(sender, instance, created, **kwargs):
    """Sync Profile changes to the linked Customer.
    
    This ensures that when you update profile details in Django Admin,
    the changes are reflected in your custom dashboard.
    """
    if not instance.user:  # Skip if no linked user
        return
    
    # Find the customer linked to this user
    try:
        customer = Customer.objects.get(user=instance.user)
    except Customer.DoesNotExist:
        return  # No customer to sync to
    
    updated = False
    
    # Sync full_name changes (handle case sensitivity)
    if instance.full_name and instance.full_name.strip() != customer.name.strip():
        customer.name = instance.full_name.strip()
        updated = True
        print(f"Profile sync: Updated customer {customer.id} name from '{customer.name}' to '{instance.full_name.strip()}'")
    
    # Sync phone changes (handle empty vs non-empty)
    if instance.phone_number != customer.phone:
        customer.phone = instance.phone_number or ''
        updated = True
    
    # Sync photo changes (profile photo becomes customer photo)
    # REMOVED: Customer model no longer has photo field
    # if instance.photo != customer.photo:
    #     customer.photo = instance.photo
    #     updated = True
    #     print(f"Profile sync: Updated customer {customer.id} photo to match profile photo")
    
    # Save customer if any changes were made
    if updated:
        customer.save(update_fields=['name', 'phone'])
        print(f"Synced profile {instance.id} changes to customer {instance.id}")

# --- Order Notifications for Admins ---
@receiver(post_save, sender='api.Order')
def create_order_notification(sender, instance, created, **kwargs):
    """Create notification when new order is placed"""
    if created:
        from .models import OrderNotification
        
        # Create new order notification
        OrderNotification.objects.create(
            notification_type='NEW_ORDER',
            title=f'New Order #{instance.order_number}',
            message=f'New order placed by {instance.user.email if instance.user else "Guest"} for ${instance.total}',
            order=instance
        )
        
        print(f"🔔 Order notification created for order #{instance.order_number}")
        
        # Send email notification to all admin users
        send_admin_order_email(instance, 'NEW_ORDER')
    
    # Also notify on status changes (but not on creation)
    elif not created and 'status' in kwargs.get('update_fields', []):
        from .models import OrderNotification
        
        # Create status change notification
        OrderNotification.objects.create(
            notification_type='ORDER_STATUS_CHANGED',
            title=f'Order #{instance.order_number} Status Updated',
            message=f'Order status changed to {instance.status}',
            order=instance
        )
        
        print(f"🔔 Status change notification created for order #{instance.order_number}")
        
        # Send email notification to all admin users
        send_admin_order_email(instance, 'ORDER_STATUS_CHANGED')

# --- Customer Deletion Synchronization ---
# REMOVED: This was causing infinite recursion
# Instead, we handle deletion synchronization in the CustomerViewSet.destroy() method

def send_admin_order_email(order, notification_type):
    """Send email notification to all admin users"""
    from django.core.mail import send_mail
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    
    User = get_user_model()
    
    # Check if admin email notifications are enabled
    if not getattr(settings, 'ADMIN_EMAIL_NOTIFICATIONS', True):
        print("📧 Admin email notifications are disabled")
        return
    
    # Get all admin users
    admin_users = User.objects.filter(is_staff=True, is_active=True)
    
    if not admin_users.exists():
        print("⚠️ No admin users found to send email notifications")
        return
    
    # Prepare email context
    dashboard_url = f"{settings.BACKEND_URL}/admin/api/order/{order.id}/change/"
    
    context = {
        'order': order,
        'notification_type': notification_type,
        'dashboard_url': dashboard_url
    }
    
    # Render HTML email template
    html_message = render_to_string('admin_order_notification.html', context)
    plain_message = strip_tags(html_message)
    
    # Prepare email content based on notification type
    if notification_type == 'NEW_ORDER':
        subject = f'🆕 New Order #{order.order_number} - Avantlush Dashboard'
    else:  # ORDER_STATUS_CHANGED
        subject = f'🔄 Order #{order.order_number} Status Updated - Avantlush Dashboard'
    
    # Send email to each admin user
    for admin_user in admin_users:
        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [admin_user.email],
                html_message=html_message,
                fail_silently=False,
            )
            print(f"📧 Email notification sent to admin: {admin_user.email}")
        except Exception as e:
            print(f"❌ Failed to send email to admin {admin_user.email}: {str(e)}")
    
    # Also send to additional admin emails if configured
    additional_emails = getattr(settings, 'ADMIN_NOTIFICATION_EMAILS', [])
    for email in additional_emails:
        if email not in [user.email for user in admin_users]:  # Avoid duplicate emails
            try:
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    html_message=html_message,
                    fail_silently=False,
                )
                print(f"📧 Email notification sent to additional admin: {email}")
            except Exception as e:
                print(f"❌ Failed to send email to additional admin {email}: {str(e)}")