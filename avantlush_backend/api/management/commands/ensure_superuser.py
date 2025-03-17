from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Ensures superusers exist'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        
        superusers = [
            {
                'email': 'samthnalyst@gmail.com',
                'password': 'Sam787878',
            },
            {
                'email': 'danieludechukwu117@gmail.com',
                'password': 'Dan1234',  
            }
        ]
        
        for superuser in superusers:
            email = superuser['email']
            password = superuser['password']
            
            if not User.objects.filter(email=email).exists():
                User.objects.create_superuser(
                    email=email,
                    password=password,
                    is_staff=True,
                    is_superuser=True
                )
                self.stdout.write(self.style.SUCCESS(f'Superuser {email} created'))
            else:
                user = User.objects.get(email=email)
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Superuser {email} updated'))