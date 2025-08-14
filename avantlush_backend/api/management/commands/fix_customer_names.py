from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from avantlush_backend.api.models import Customer

class Command(BaseCommand):
    help = "Fix customer names that are currently email addresses"

    def handle(self, *args, **options):
        User = get_user_model()
        updated_count = 0
        
        for customer in Customer.objects.all():
            if customer.user and '@' in customer.name:
                # Customer has email as name, try to fix it
                user = customer.user
                
                if user.first_name and user.last_name:
                    new_name = f"{user.first_name} {user.last_name}".strip()
                elif user.first_name:
                    new_name = user.first_name.strip()
                elif user.last_name:
                    new_name = user.last_name.strip()
                else:
                    # Fallback: use email prefix as name
                    email_prefix = user.email.split('@')[0]
                    new_name = email_prefix.replace('.', ' ').replace('_', ' ').title()
                
                if new_name != customer.name:
                    old_name = customer.name
                    customer.name = new_name
                    customer.save(update_fields=["name"])
                    updated_count += 1
                    self.stdout.write(f"Updated customer {customer.id}: '{old_name}' -> '{new_name}'")
        
        self.stdout.write(self.style.SUCCESS(f"Fixed {updated_count} customer names"))
