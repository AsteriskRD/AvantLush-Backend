"""
Django settings for avantlush_backend project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api
from pathlib import WindowsPath
import os

load_dotenv()  # Load environment variables

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your-default-secret-key-for-dev')

DEBUG = True  # Temporarily set to True for testing

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',
    '.ngrok-free.app',
    'avantlush-backend-13.onrender.com',
    'avantlush-backend-2s6k.onrender.com'  # Fixed
]

#Https handling
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True if os.getenv('SECURE_SSL_REDIRECT') == 'True' else False

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',  
    'django.contrib.sites',
    
    # Cloudinary
    'cloudinary_storage',
    'cloudinary',
    
    # Local
    'avantlush_backend.api',  
     
    # Third party
    'rest_framework',
    'django_filters',
    'rest_framework.authtoken',
    'corsheaders',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',
    'checkout',
    
    # Allauth and registration
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.apple',
    'dj_rest_auth',
    'dj_rest_auth.registration',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    'allauth.account.middleware.AccountMiddleware',
    #'avantlush_backend.api.middleware.StandardizedResponseMiddleware',
]

AUTH_USER_MODEL = 'api.CustomUser'

ROOT_URLCONF = 'avantlush_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'api/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '706871150237-rou6sud1lbelvim0u49bmkcp80k1eudo.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'

# Add these settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': '706871150237-rou6sud1lbelvim0u49bmkcp80k1eudo.apps.googleusercontent.com',
            'secret': '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',
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# Apple provider settings
SOCIALACCOUNT_PROVIDERS = {
    'apple': {
        'APP': {
            'client_id': 'your.apple.client.id',
            'secret': 'your.apple.secret',
            'key': 'your.apple.key',
        },
        'SCOPE': ['email', 'name'],
        'TEAM_ID': 'your.apple.team.id',
        'KEY_ID': 'your.apple.key.id',
        'CERTIFICATE_KEY': """-----BEGIN PRIVATE KEY-----
Your private key here
-----END PRIVATE KEY-----"""
    }
}

#Payment methods
CLOVER_PUBLIC_TOKEN = '57c5f8cf1e22bd2cf97a95db31080287'
CLOVER_PRIVATE_TOKEN = '7f340fd7-6aff-16c8-4740-a3cc8b811a6b'
STRIPE_PUBLIC_KEY = 'your_stripe_public_key'
STRIPE_SECRET_KEY = 'your_stripe_secret_key'
PAYPAL_MODE = 'sandbox'  # sandbox or live
PAYPAL_CLIENT_ID = 'dummy_client_id'
PAYPAL_CLIENT_SECRET = 'dummy_client_secret'
GOOGLE_PAY_MERCHANT_ID = 'your_google_pay_merchant_id'

# Apple OAuth2 settings
APPLE_OAUTH2_CALLBACK_URL = 'your-callback-url'
APPLE_OAUTH2_CLIENT_ID = 'your-client-id'
APPLE_OAUTH2_CLIENT_SECRET = 'your-client-secret'
APPLE_OAUTH2_KEY_ID = 'your-key-id'
APPLE_OAUTH2_TEAM_ID = 'your-team-id'
APPLE_OAUTH2_PRIVATE_KEY = '''your-private-key'''

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True

WSGI_APPLICATION = 'avantlush_backend.wsgi.application'

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Database configuration
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True,  # Add health checks for better reliability
    )
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

#FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')  # Updated to new port
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

# For Render deployment
if 'RENDER' in os.environ:
    BACKEND_URL = 'https://avantlush-backend-2s6k.onrender.com'

# Google OAuth2 settings
# Instead of hardcoding the callback URL, I'm using an environment variable
GOOGLE_OAUTH2_CALLBACK_URL = os.getenv('GOOGLE_OAUTH2_CALLBACK_URL', f'{FRONTEND_URL}/auth/google/callback')
APPLE_OAUTH2_CALLBACK_URL = os.getenv('APPLE_OAUTH2_CALLBACK_URL', f'{FRONTEND_URL}/auth/apple/callback')
REST_USE_JWT = True
REST_AUTH_SERIALIZERS = {
    'LOGIN_SERIALIZER': 'avantlush_backend.api.serializers.GoogleAuthSerializer',
}

REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'my-app-auth',
    'JWT_AUTH_REFRESH_COOKIE': 'my-refresh-token',
    'JWT_AUTH_HTTPONLY': False,  # Set to False if needs to access the token in JavaScript
    'USER_DETAILS_SERIALIZER': 'avantlush_backend.api.serializers.CustomUserDetailsSerializer',
    'LOGIN_SERIALIZER': 'avantlush_backend.api.serializers.LoginSerializer',
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Use WhiteNoise for static files in production
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

print("BASE_DIR:", BASE_DIR)
print("STATIC_ROOT:", os.path.join(BASE_DIR, 'staticfiles'))
print("STATICFILES_DIRS:", [os.path.join(BASE_DIR, 'static')])
print(f"Does static dir exist? {os.path.exists(BASE_DIR / 'static')}")
print(f"Does staticfiles dir exist? {os.path.exists(STATIC_ROOT)}")
# Media files (uploaded images, videos)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB per image

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dvfwa8fzh',
    'API_KEY': '345125992849241',
    'API_SECRET': '2ZGsMf9ofeLgqpWdgYHRzK1QWM8'
}

cloudinary.config( 
    cloud_name = 'dvfwa8fzh',
    api_key = '345125992849241', 
    api_secret = '2ZGsMf9ofeLgqpWdgYHRzK1QWM8'
)
# Configure the default file storage to use Cloudinary
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '5/minute',
    }

}


CORS_ALLOW_ALL_ORIGINS = True  # For development only

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken']
CORS_ALLOW_CREDENTIALS = True

# CORS settings
#CORS_ALLOWED_ORIGINS = [
#    'http://localhost:5173',
#    'http://localhost:3000',
#    'http://127.0.0.1:5173',
#    'https://avantlush.com',
#    'https://avantlush-backend-13.onrender.com',
#    'https://avantlush-backend-2s6k.onrender.com'  # Fixed
#]
# Security settings
SECURE_SSL_REDIRECT =  False        #os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Use database-backed sessions
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_SAVE_EVERY_REQUEST = True  # Save the session to the database on every request

# In development, use Lax same-site policy for cookies
if DEBUG:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_HTTPONLY = False
    CSRF_USE_SESSIONS = False

# Email settings
# Development configuration for testing
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465  # Changed to SSL port
EMAIL_USE_SSL = True  # Enable SSL
EMAIL_USE_TLS = False  # Disable TLS since we're using SSL
EMAIL_HOST_USER = 'avalusht@gmail.com'
EMAIL_HOST_PASSWORD = 'ojgrpofmppisffdr'
DEFAULT_FROM_EMAIL = 'avalusht@gmail.com'
EMAIL_TIMEOUT = 20
SERVER_EMAIL = 'avalusht@gmail.com'

#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#        'LOCATION': 'redis://127.0.0.1:6379/1',
#    }
#}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}




print("Current directory:", os.getcwd())
print("BASE_DIR:", BASE_DIR)
print("STATIC_ROOT:", STATIC_ROOT)
print("STATICFILES_DIRS:", STATICFILES_DIRS)
