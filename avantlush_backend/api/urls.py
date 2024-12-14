from django.urls import path
from .views import waitlist_signup, api_root

urlpatterns = [
    path('', api_root, name='api-root'),
    path('waitlist/signup/', waitlist_signup, name='waitlist-signup'),
]
