from api.models import CustomUser
CustomUser.objects.all().values('email')