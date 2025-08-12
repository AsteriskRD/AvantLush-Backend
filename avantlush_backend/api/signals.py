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
        display_name = instance.get_full_name().strip() or instance.email
        Customer.objects.create(
            user=instance,
            name=display_name,
            email=instance.email,
        )
        return

    # Keep name up to date if the customer has a placeholder name and user now has a better one
    preferred_name = (instance.get_full_name() or '').strip()
    if preferred_name and customer.name != preferred_name:
        customer.name = preferred_name
        customer.save(update_fields=["name"])