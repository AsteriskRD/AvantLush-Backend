from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from avantlush_backend.api.models import Customer, Profile

User = get_user_model()

class Command(BaseCommand):
    help = "Test bidirectional sync between CustomUser, Profile, and Customer models"

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Test sync for a specific user ID'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Test sync for a specific email'
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        email = options.get('email')
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                self.test_user_sync(user)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with ID {user_id} not found'))
        elif email:
            try:
                user = User.objects.get(email=email)
                self.test_user_sync(user)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with email {email} not found'))
        else:
            # Test all users
            users = User.objects.all()[:5]  # Limit to first 5 users
            for user in users:
                self.test_user_sync(user)
                self.stdout.write('-' * 50)

    def test_user_sync(self, user):
        """Test sync for a specific user"""
        self.stdout.write(f"\n🔍 Testing sync for User: {user.email}")
        self.stdout.write(f"   ID: {user.id}")
        self.stdout.write(f"   First Name: {user.first_name}")
        self.stdout.write(f"   Last Name: {user.last_name}")
        self.stdout.write(f"   Is Active: {user.is_active}")
        
        # Check Profile
        try:
            profile = Profile.objects.get(user=user)
            self.stdout.write(f"   Profile Full Name: {profile.full_name}")
            self.stdout.write(f"   Profile Phone: {profile.phone_number}")
        except Profile.DoesNotExist:
            self.stdout.write(self.style.WARNING("   ❌ No Profile found"))
            profile = None
        
        # Check Customer
        try:
            customer = Customer.objects.get(user=user)
            self.stdout.write(f"   Customer Name: {customer.name}")
            self.stdout.write(f"   Customer Email: {customer.email}")
            self.stdout.write(f"   Customer Phone: {customer.phone}")
            self.stdout.write(f"   Customer Status: {customer.status}")
        except Customer.DoesNotExist:
            self.stdout.write(self.style.WARNING("   ❌ No Customer found"))
            customer = None
        
        # Check for inconsistencies
        if profile and customer:
            name_consistent = profile.full_name == customer.name
            phone_consistent = profile.phone_number == customer.phone
            email_consistent = user.email == customer.email
            status_consistent = user.is_active == (customer.status == 'active')
            
            self.stdout.write(f"\n   📊 Sync Status:")
            self.stdout.write(f"      Name: {'✅' if name_consistent else '❌'} (Profile: {profile.full_name}, Customer: {customer.name})")
            self.stdout.write(f"      Phone: {'✅' if phone_consistent else '❌'} (Profile: {profile.phone_number}, Customer: {customer.phone})")
            self.stdout.write(f"      Email: {'✅' if email_consistent else '❌'} (User: {user.email}, Customer: {customer.email})")
            self.stdout.write(f"      Status: {'✅' if status_consistent else '❌'} (User: {user.is_active}, Customer: {customer.status})")
            
            if not all([name_consistent, phone_consistent, email_consistent, status_consistent]):
                self.stdout.write(self.style.WARNING("   ⚠️  Inconsistencies detected!"))
            else:
                self.stdout.write(self.style.SUCCESS("   ✅ All fields are in sync!"))
        else:
            self.stdout.write(self.style.ERROR("   ❌ Cannot check sync - missing Profile or Customer"))
