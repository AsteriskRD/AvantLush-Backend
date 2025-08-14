from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from avantlush_backend.api.models import Customer, Profile

User = get_user_model()

class Command(BaseCommand):
    help = "Debug specific user sync issues"

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email of user to debug'
        )

    def handle(self, *args, **options):
        email = options.get('email')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with email {email} not found'))
            return
        
        self.stdout.write(f"\n🔍 Debugging sync for User: {user.email}")
        self.stdout.write(f"   ID: {user.id}")
        self.stdout.write(f"   First Name: '{user.first_name}'")
        self.stdout.write(f"   Last Name: '{user.last_name}'")
        self.stdout.write(f"   Is Active: {user.is_active}")
        
        # Check Profile
        try:
            profile = Profile.objects.get(user=user)
            self.stdout.write(f"\n📋 Profile Details:")
            self.stdout.write(f"   ID: {profile.id}")
            self.stdout.write(f"   Full Name: '{profile.full_name}'")
            self.stdout.write(f"   Phone: '{profile.phone_number}'")
            self.stdout.write(f"   Updated At: {profile.updated_at}")
        except Profile.DoesNotExist:
            self.stdout.write(self.style.WARNING("   ❌ No Profile found"))
            profile = None
        
        # Check Customer
        try:
            customer = Customer.objects.get(user=user)
            self.stdout.write(f"\n👤 Customer Details:")
            self.stdout.write(f"   ID: {customer.id}")
            self.stdout.write(f"   Name: '{customer.name}'")
            self.stdout.write(f"   Email: '{customer.email}'")
            self.stdout.write(f"   Phone: '{customer.phone}'")
            self.stdout.write(f"   Status: '{customer.status}'")
            self.stdout.write(f"   Created At: {customer.created_at}")
        except Customer.DoesNotExist:
            self.stdout.write(self.style.WARNING("   ❌ No Customer found"))
            customer = None
        
        if profile and customer:
            self.stdout.write(f"\n🔍 Sync Analysis:")
            
            # Check name sync
            name_match = profile.full_name.strip() == customer.name.strip()
            self.stdout.write(f"   Name Match: {'✅' if name_match else '❌'}")
            if not name_match:
                self.stdout.write(f"      Profile: '{profile.full_name.strip()}'")
                self.stdout.write(f"      Customer: '{customer.name.strip()}'")
                self.stdout.write(f"      Length diff: {len(profile.full_name.strip())} vs {len(customer.name.strip())}")
                self.stdout.write(f"      ASCII diff: {[ord(c) for c in profile.full_name.strip()]} vs {[ord(c) for c in customer.name.strip()]}")
            
            # Check phone sync
            phone_match = profile.phone_number == customer.phone
            self.stdout.write(f"   Phone Match: {'✅' if phone_match else '❌'}")
            if not phone_match:
                self.stdout.write(f"      Profile: '{profile.phone_number}'")
                self.stdout.write(f"      Customer: '{customer.phone}'")
            
            # Check status sync
            status_match = (user.is_active and customer.status == 'active') or (not user.is_active and customer.status == 'blocked')
            self.stdout.write(f"   Status Match: {'✅' if status_match else '❌'}")
            if not status_match:
                self.stdout.write(f"      User.is_active: {user.is_active}")
                self.stdout.write(f"      Customer.status: '{customer.status}'")
            
            # Test manual sync
            self.stdout.write(f"\n🧪 Testing Manual Sync:")
            if not name_match:
                self.stdout.write(f"   Would update customer name from '{customer.name}' to '{profile.full_name.strip()}'")
                # Actually do the update
                old_name = customer.name
                customer.name = profile.full_name.strip()
                customer.save(update_fields=['name'])
                self.stdout.write(f"   ✅ Updated customer name: '{old_name}' → '{customer.name}'")
            
            if not phone_match:
                self.stdout.write(f"   Would update customer phone from '{customer.phone}' to '{profile.phone_number}'")
                old_phone = customer.phone
                customer.phone = profile.phone_number or ''
                customer.save(update_fields=['phone'])
                self.stdout.write(f"   ✅ Updated customer phone: '{old_phone}' → '{customer.phone}'")
            
            if not status_match:
                expected_status = 'active' if user.is_active else 'blocked'
                self.stdout.write(f"   Would update customer status from '{customer.status}' to '{expected_status}'")
                old_status = customer.status
                customer.status = expected_status
                customer.save(update_fields=['status'])
                self.stdout.write(f"   ✅ Updated customer status: '{old_status}' → '{customer.status}'")
        
        self.stdout.write(f"\n✅ Debug complete for {user.email}")
