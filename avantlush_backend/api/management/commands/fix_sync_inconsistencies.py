from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from avantlush_backend.api.models import Customer, Profile

User = get_user_model()

class Command(BaseCommand):
    help = "Fix existing sync inconsistencies between CustomUser, Profile, and Customer models"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING("🔍 DRY RUN MODE - No changes will be made"))
        
        self.stdout.write("🔧 Fixing sync inconsistencies...")
        
        fixed_count = 0
        total_users = 0
        
        for user in User.objects.all():
            total_users += 1
            user_fixed = self.fix_user_sync(user, dry_run)
            if user_fixed:
                fixed_count += 1
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"✅ DRY RUN COMPLETE: Would fix {fixed_count} out of {total_users} users"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ SYNC FIX COMPLETE: Fixed {fixed_count} out of {total_users} users"))

    def fix_user_sync(self, user, dry_run=False):
        """Fix sync issues for a specific user"""
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            self.stdout.write(f"   ❌ User {user.email} has no Profile")
            return False
        
        try:
            customer = Customer.objects.get(user=user)
        except Customer.DoesNotExist:
            self.stdout.write(f"   ❌ User {user.email} has no Customer")
            return False
        
        fixed = False
        changes = []
        
        # Fix name inconsistencies
        if profile.full_name and profile.full_name.strip() != customer.name.strip():
            old_name = customer.name
            new_name = profile.full_name.strip()
            changes.append(f"Customer name: '{old_name}' → '{new_name}'")
            if not dry_run:
                customer.name = new_name
            fixed = True
        
        # Fix phone inconsistencies
        if profile.phone_number != customer.phone:
            old_phone = customer.phone
            new_phone = profile.phone_number or ''
            changes.append(f"Customer phone: '{old_phone}' → '{new_phone}'")
            if not dry_run:
                customer.phone = new_phone
            fixed = True
        
        # Fix status inconsistencies
        expected_status = 'active' if user.is_active else 'blocked'
        if customer.status != expected_status:
            old_status = customer.status
            new_status = expected_status
            changes.append(f"Customer status: '{old_status}' → '{new_status}'")
            if not dry_run:
                customer.status = new_status
            fixed = True
        
        # Fix user name inconsistencies (if customer has better name)
        if customer.name and not user.get_full_name().strip():
            # Parse customer name into first_name and last_name
            name_parts = customer.name.strip().split(' ', 1)
            if len(name_parts) == 1:
                if user.first_name != name_parts[0]:
                    changes.append(f"User first_name: '{user.first_name}' → '{name_parts[0]}'")
                    if not dry_run:
                        user.first_name = name_parts[0]
                        user.last_name = ''
                    fixed = True
            else:
                first_name, last_name = name_parts
                if user.first_name != first_name or user.last_name != last_name:
                    changes.append(f"User names: '{user.first_name} {user.last_name}' → '{first_name} {last_name}'")
                    if not dry_run:
                        user.first_name = first_name
                        user.last_name = last_name
                    fixed = True
        
        if fixed:
            if not dry_run:
                # Save changes
                customer.save(update_fields=['name', 'phone', 'status'])
                user.save(update_fields=['first_name', 'last_name'])
            
            self.stdout.write(f"   🔧 Fixed {user.email}:")
            for change in changes:
                self.stdout.write(f"      {change}")
        
        return fixed
