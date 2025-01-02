from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import waitlist_signup, api_root, register, login, preview_email
from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path
from . import views

urlpatterns = [
    path('', api_root),
    path('waitlist/signup/', waitlist_signup, name='waitlist_signup'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('preview-email/', preview_email, name='preview_email'),
    path('accounts/', include('allauth.urls')),
    path('auth/google/', views.google_auth, name='google_auth'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
