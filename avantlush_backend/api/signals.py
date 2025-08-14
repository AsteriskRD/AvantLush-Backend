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