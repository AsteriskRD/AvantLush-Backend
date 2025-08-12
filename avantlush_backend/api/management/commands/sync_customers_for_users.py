from django.core.management.base import BaseCommand
from django.conf import settings

from avantlush_backend.api.models import Customer
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Ensure every user has a corresponding Customer row and link by email if missing."

    def handle(self, *args, **options):
        User = get_user_model()
        created_count = 0
        linked_count = 0
        updated_name = 0

        for user in User.objects.all():
            customer = Customer.objects.filter(user=user).first()
            if customer is None:
                # Try link by email
                customer = Customer.objects.filter(email__iexact=user.email).first()
                if customer is not None:
                    if customer.user is None:
                        customer.user = user
                        customer.save(update_fields=["user"])
                        linked_count += 1
                else:
                    # Create new
                    name = (user.get_full_name() or user.email).strip()
                    Customer.objects.create(user=user, name=name, email=user.email)
                    created_count += 1
                    continue

            # Sync name if needed
            preferred_name = (user.get_full_name() or '').strip()
            if preferred_name and customer and customer.name != preferred_name:
                customer.name = preferred_name
                customer.save(update_fields=["name"])
                updated_name += 1

        self.stdout.write(self.style.SUCCESS(
            f"Customers sync complete. created={created_count}, linked={linked_count}, updated_name={updated_name}"
        ))


