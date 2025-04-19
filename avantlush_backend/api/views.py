# Django imports
import requests
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.db.models import Q
from datetime import datetime
import csv
from django.apps import apps
from django.http import HttpResponse
from django.contrib.auth import get_user_model


from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.utils import timezone
from django.db.models import Count, Sum, F, Q
from django.db.models.functions import TruncDate
from datetime import timedelta

from .models import SupportTicket, TicketResponse

# Rest Framework imports
from rest_framework import status, filters, viewsets, generics, mixins
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    action,
    api_view,
    permission_classes,
    throttle_classes
)
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

# Third party imports
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
from google.oauth2 import id_token
#from google.auth.transport import requests
import stripe
import uuid
from decimal import Decimal
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework_simplejwt.tokens import RefreshToken


# Local imports - Models
from .models import (
    Address,
    Article,
    Cart,
    CartItem,
    CustomUser,
    EmailVerificationToken,
    Order,
    PasswordResetToken,
    Payment,
    Product,
    ProductRecommendation,
    Profile,
    Review,
    ReviewHelpfulVote,
    ReviewTag,
    ShippingMethod,
    WaitlistEntry,
    Wishlist,
    WishlistItem,
    Tag,
    Category,
    Customer,
    OrderItem,
    CarouselItem,
    Size,
    Color
    
)

# Local imports - Serializers
from .serializers import (
    AddressSerializer,
    AppleAuthSerializer,
    ArticleSerializer,
    CartItemSerializer,
    CartSerializer,
    ForgotPasswordSerializer,
    GoogleAuthSerializer,
    LoginSerializer,
    OrderSerializer,
    ProductRecommendationSerializer,
    ProductSerializer,
    ProfileSerializer,
    RegistrationSerializer,
    ResetPasswordSerializer,
    ReviewSerializer,
    ShippingMethodSerializer,
    WaitlistSerializer,
    WishlistItemSerializer,
    WishlistSerializer,
    SupportTicketSerializer, 
    TicketResponseSerializer,
    DashboardCartMetricsSerializer,
    DashboardCustomerMetricsSerializer,
    DashboardOrderMetricsSerializer,
    DashboardSalesTrendSerializer,
    DashboardRecentOrderSerializer,
    ProductManagementSerializer,
    TagSerializer,
    CategorySerializer,
    ReviewSummarySerializer,
    OrderCreateSerializer,
    OrderItemSerializer,
    CustomerSerializer,
    CustomerDetailSerializer,
    CustomerCreateSerializer,
    CarouselItemSerializer,
    UserDetailsUpdateSerializer,
    CarouselItemPublicSerializer,
    SizeSerializer,
    ColorSerializer,
    
    
)

# Filters impors
from .filter import OrderFilter

# Local imports - Services
from .services import CloverPaymentService
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Sum, F, Q
from django.db.models.functions import TruncDate
from datetime import timedelta
from django_filters import FilterSet
from django_filters import DateFromToRangeFilter
from django_filters import FilterSet, NumberFilter
from .models import Order, SavedPaymentMethod
from .services import CloverPaymentService

class WaitlistRateThrottle(AnonRateThrottle):
    rate = '5/minute'  # Limit to 5 requests per minute per IP

User = get_user_model()

def get_verification_url(user, token):
    """Generate verification URL for both local and production environments"""
    backend_url = settings.BACKEND_URL
    frontend_url = settings.FRONTEND_URL
    production_frontend_url = "https://avantlush.com"
    
    # Encode user ID for the URL
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Create the verification paths
    backend_path = f"{backend_url}/api/verify-email/{token}/{uid}"
    local_frontend_path = f"{frontend_url}/verify-email/{token}/{uid}"
    production_frontend_path = f"{production_frontend_url}/verify-email/{token}/{uid}"
    
    return {
        'backend_url': backend_path,
        'frontend_url': local_frontend_path,
        'production_frontend_url': production_frontend_path
    }
class GoogleLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GoogleAuthSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            location = serializer.validated_data.get('location', 'Nigeria')
            
            try:
                # Print debugging info
                print(f"Attempting to verify token with client ID: {settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY}")
                
                # For testing purposes, you can try both verification methods
                try:
                    # Method 1: Using google-auth library
                    idinfo = id_token.verify_oauth2_token(
                        token,
                        google_requests.Request(),
                        settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
                    )
                    print("Token verified successfully with google-auth!")
                    print(f"Token info: {idinfo}")
                except Exception as e1:
                    print(f"google-auth verification failed: {str(e1)}")
                    
                    # Method 2: Using requests to validate with Google's tokeninfo endpoint
                    response = requests.get(
                        f'https://oauth2.googleapis.com/tokeninfo?id_token={token}'
                    )
                    if response.status_code == 200:
                        idinfo = response.json()
                        print("Token verified successfully with tokeninfo endpoint!")
                        print(f"Token info: {idinfo}")
                    else:
                        print(f"tokeninfo verification failed: {response.text}")
                        raise ValueError("Token verification failed with both methods")
                
                # Check if the token is issued by Google
                if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    print(f"Invalid issuer: {idinfo['iss']}")
                    return Response(
                        {"error": "Invalid token issuer"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Extract user information from the verified token
                google_id = idinfo['sub']
                email = idinfo['email']
                name = idinfo.get('name', '')
                first_name = idinfo.get('given_name', '')
                last_name = idinfo.get('family_name', '')
                
                print(f"Extracted user info - Email: {email}, Name: {name}, First: {first_name}, Last: {last_name}, Google ID: {google_id}")
                
                # Check if user exists with this email
                try:
                    user = CustomUser.objects.get(email=email)
                    print(f"Existing user found with email: {email}")
                    # Update Google ID if not already set
                    if not user.google_id:
                        user.google_id = google_id
                        user.save()
                    
                    # Always update the profile with the name from Google
                    profile, created = Profile.objects.get_or_create(user=user)
                    if name:  # If name is available from Google
                        profile.full_name = name
                        profile.save()
                        print(f"Updated profile name to: {name}")
                        
                except CustomUser.DoesNotExist:
                    # Create a new user
                    print(f"Creating new user with email: {email}")
                    user = CustomUser.objects.create_user(
                        email=email,
                        location=location,
                        google_id=google_id
                    )
                    # Create profile with name from Google
                    profile, created = Profile.objects.get_or_create(user=user)
                    if name:
                        profile.full_name = name
                        profile.save()
                        print(f"Created profile with name: {name}")
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                # Get the user's profile (it should be updated with the Google name)
                profile = None
                try:
                    profile = user.profile
                except:
                    pass

                # Build the response
                user_data = {
                    'email': user.email,
                    'location': user.location,
                    'uuid': user.uuid
                }

                # Add profile data if available
                if profile:
                    user_data['full_name'] = profile.full_name
                    # Add any other profile fields you want to include
                    if hasattr(profile, 'photo') and profile.photo:
                        user_data['photo_url'] = profile.photo.url
                    
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': user_data
                })
                
            except ValueError as ve:
                # Invalid token
                print(f"ValueError during token verification: {str(ve)}")
                return Response(
                    {"error": "Invalid token", "details": str(ve)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                # Log the error for debugging
                print(f"Google authentication error: {str(e)}")
                import traceback
                traceback.print_exc()
                return Response(
                    {"error": "Authentication failed", "details": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class AppleLoginView(SocialLoginView):
    adapter_class = AppleOAuth2Adapter
    callback_url = settings.APPLE_OAUTH2_CALLBACK_URL
    client_class = OAuth2Client
    serializer_class = AppleAuthSerializer

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
@api_view(['GET'])
def api_root(request):
    return Response({
        'status': 'API is running',
        'available_endpoints': {
            'waitlist_signup': '/api/waitlist/signup/',
            'register': '/api/register/',
            'login': '/api/login/',
            'admin': '/admin/',
            'products': '/api/products/',
            'products_detail': '/api/products/<int:pk>/',
            'articles': '/api/articles/',
            'articles_detail': '/api/articles/<int:pk>/',
            'cart': '/api/cart/',
            'cart_items': '/api/cart/items/',
            'orders': '/api/orders/',
            'orders_detail': '/api/orders/<int:pk>/',
            'orders_update_status': '/api/orders/<int:pk>/status/',
        }
    })


@api_view(['POST'])
@throttle_classes([WaitlistRateThrottle])
def waitlist_signup(request):
    try:
        serializer = WaitlistSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Try to create the waitlist entry
                waitlist_entry = serializer.save()

                # Prepare email context with Cloudinary URLs
                context = {
                    'email': waitlist_entry.email,
                    'CLOUDINARY_URLS': {
                        'logo': 'https://res.cloudinary.com/dvfwa8fzh/image/upload/v1736339705/avantlush-email/Avantlush%20logo.svg',
                        'menu': 'https://res.cloudinary.com/dvfwa8fzh/image/upload/v1736339712/avantlush-email/menu.svg',
                        'share': 'https://res.cloudinary.com/dvfwa8fzh/image/upload/v1736339714/avantlush-email/share.svg',
                        'facebook': 'https://res.cloudinary.com/dvfwa8fzh/image/upload/v1736339707/avantlush-email/Facebook.svg',
                        'linkedin': 'https://res.cloudinary.com/dvfwa8fzh/image/upload/v1736339710/avantlush-email/Linkedin.svg',
                        'twitter': 'https://res.cloudinary.com/dvfwa8fzh/image/upload/v1736339719/avantlush-email/Twitter.svg',
                        'instagram': 'https://res.cloudinary.com/dvfwa8fzh/image/upload/v1736339709/avantlush-email/Instagram.svg',
                        'template1': 'https://res.cloudinary.com/dvfwa8fzh/image/upload/v1736339717/avantlush-email/template1.png',
                        'template2': 'https://res.cloudinary.com/dvfwa8fzh/image/upload/v1736339717/avantlush-email/template2.png',
                        'template3': 'https://res.cloudinary.com/dvfwa8fzh/image/upload/v1736339718/avantlush-email/template3.png'
                    }
                }

                html_message = render_to_string('waitlist-email.html', context)
                plain_message = strip_tags(html_message)

                send_mail(
                    'Thank You For Joining The Avantlush Waitlist',
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [waitlist_entry.email],
                    html_message=html_message,
                    fail_silently=False,
                )

                response_data = {
                    'success': True,
                    'message': 'Successfully added to waitlist',
                    'email': waitlist_entry.email,
                    'statusCode': status.HTTP_201_CREATED
                }

                return Response(
                    response_data,
                    status=status.HTTP_201_CREATED
                )

            except IntegrityError:
                response_data = {
                    'success': False,
                    'message': 'Waitlist entry with this email already exists',
                    'email': serializer.validated_data['email'],
                    'statusCode': status.HTTP_409_CONFLICT
                }
                return Response(
                    response_data,
                    status=status.HTTP_409_CONFLICT
                )

        # Handle validation errors
        response_data = {
            'success': False,
            'message': 'Validation error',
            'errors': serializer.errors,
            'statusCode': status.HTTP_400_BAD_REQUEST
        }
        return Response(
            response_data,
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        response_data = {
            'success': False,
            'message': 'An error occurred',
            'error': str(e),
            'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR
        }
        return Response(
            response_data,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(['GET'])
def preview_email(request):
    return render(request, 'waitlist-email.html')

# Update register function:
@api_view(['POST'])
def register(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Create user but set as inactive until email verification
            user = serializer.save(is_active=False)
            
            # Create verification token
            verification_token = EmailVerificationToken.objects.create(user=user)
            
            # Get verification URLs - both backend and frontend
            verification_urls = get_verification_url(
                user, 
                verification_token.token
            )
                        
            # Prepare email context with both URLs
            context = {
                'verification_url': verification_urls['frontend_url'],
                'production_verification_url': verification_urls['production_frontend_url'],
                'backend_verification_url': verification_urls['backend_url'],
                'location': user.location,
            }
            
            # Send verification email
            try:
                html_message = render_to_string('email_verification.html', context)
                plain_message = strip_tags(html_message)
                
                send_mail(
                    'Verify Your Email - Avantlush',
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
            except Exception as email_error:
                print(f"Email sending failed: {str(email_error)}")
                
            return Response({
                'success': True,
                'message': 'Registration successful. Please check your email to verify your account.',
                'email': user.email,
                'id': str(user.uuid),
                'location': user.location,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Registration failed: {str(e)}")
            return Response({
                'success': False,
                'message': 'Registration failed',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'success': False,
        'message': 'Invalid data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, uidb64, token):
    try:
        # Decode the user ID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
        
        # Get the verification token
        try:
            verification_token = EmailVerificationToken.objects.get(
                user=user,
                token=token,  # Remove UUID conversion
                is_used=False
            )
        except EmailVerificationToken.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid verification token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if token is valid (not expired)
        if not verification_token.is_valid:
            return Response({
                'success': False,
                'message': 'Verification link has expired'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Activate user and mark token as used
        user.is_active = True
        user.save()
        
        verification_token.is_used = True
        verification_token.save()
        
        # Create auth token for automatic login
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'success': True,
            'message': 'Email verified successfully',
            'token': token.key
        }, status=status.HTTP_200_OK)
        
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist) as e:
        print(f"Verification error: {str(e)}")  # Add logging
        return Response({
            'success': False,
            'message': 'Invalid verification link'
        }, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_email(request):
    try:
        email = request.data.get('email')
        user = CustomUser.objects.get(email=email, is_active=False)
        
        # Delete old token if exists
        EmailVerificationToken.objects.filter(user=user).delete()
        
        # Create new verification token
        verification_token = EmailVerificationToken.objects.create(user=user)
        
       # Get verification URLs - both backend and frontend
        verification_urls = get_verification_url(
            user, 
            verification_token.token
        )
                
        # Prepare email context with both URLs
        context = {
            'verification_url': verification_urls['frontend_url'],
            'production_verification_url': verification_urls['production_frontend_url'],
            'backend_verification_url': verification_urls['backend_url'],
            'location': user.location if hasattr(user, 'location') else None,
        }
        # Render email template
        html_message = render_to_string('email_verification.html', context)
        plain_message = strip_tags(html_message)
        
        # Send verification email
        send_mail(
            'Verify Your Email - Avantlush',
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return Response({
            'success': True,
            'message': 'Verification email resent successfully'
        }, status=status.HTTP_200_OK)
        
    except CustomUser.DoesNotExist:
        return Response({
            'success': False,
            'message': 'No unverified user found with this email'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = authenticate(request, email=email, password=password)
        
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'success': True,
                'token': token.key,
                'id': user.id,
                'email': user.email,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
            
        return Response({
            'success': False,
            'message': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
        
    return Response({
        'success': False,
        'message': 'Invalid data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@action(detail=False, methods=['get'])
def featured(self, request):
    featured_products = self.get_queryset().filter(is_featured=True)
    serializer = self.get_serializer(featured_products, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = CustomUser.objects.get(email=email)
            
            # Delete any existing reset token
            PasswordResetToken.objects.filter(user=user).delete()
            
            # Create new reset token
            reset_token = PasswordResetToken.objects.create(user=user)
            
            # Encode user ID
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create both local and production reset URLs
            local_reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{reset_token.token}"
            production_reset_url = f"https://avantlush.com/reset-password/{uid}/{reset_token.token}"
            
            # Prepare email context
            context = {
                'reset_url': local_reset_url,
                'production_reset_url': production_reset_url,
                'user_email': user.email
            }
            
            # Send reset email
            html_message = render_to_string('password_reset_email.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                'Reset Your Password - Avantlush',
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return Response({
                'success': True,
                'message': 'Password reset instructions have been sent to your email. Please check both your inbox and spam folder.'
            }, status=status.HTTP_200_OK)
            
        except CustomUser.DoesNotExist:
            # Return error message when email doesn't exist
            return Response({
                'success': False,
                'message': 'Your account does not exist'
            }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'success': False,
        'message': 'Invalid data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request, uidb64, token):
    try:
        # Decode the user ID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
        
        # Get the reset token
        reset_token = PasswordResetToken.objects.get(
            user=user,
        #    token=uuid.UUID(token),
            is_used=False
        )
        
        # Check if token is valid
        if not reset_token.is_valid:
            return Response({
                'success': False,
                'message': 'Reset link has expired'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate and set new password
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            # Important: Use set_password() to properly hash the password
            new_password = serializer.validated_data['password']
            user.set_password(new_password)
            user.save()
            
            # Mark token as used
            reset_token.is_used = True
            reset_token.save()
            
            # Delete any existing auth tokens for this user
            Token.objects.filter(user=user).delete()
            
            # Create new auth token
            new_token = Token.objects.create(user=user)
            
            # Try to authenticate with new password to verify it works
            auth_user = authenticate(email=user.email, password=new_password)
            if auth_user is None:
                return Response({
                    'success': False,
                    'message': 'Password reset failed - authentication error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'success': True,
                'message': 'Password reset successful',
                'token': new_token.key
            }, status=status.HTTP_200_OK)
            
        return Response({
            'success': False,
            'message': 'Invalid password',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except (TypeError, ValueError, OverflowError, ObjectDoesNotExist) as e:
        return Response({
            'success': False,
            'message': f'Invalid reset link: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
class TokenValidationView(APIView):
    """
    API endpoint to check if a JWT token is still valid and get its expiry time.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        
        if not token:
            return Response({
                'success': False,
                'message': 'Token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Decode the token without verifying signature first
            access_token = AccessToken(token)
            
            # Check if the token is expired
            expiry_timestamp = access_token.payload.get('exp')
            current_timestamp = datetime.now().timestamp()
            
            if expiry_timestamp < current_timestamp:
                return Response({
                    'success': False,
                    'message': 'Token has expired',
                    'expired': True
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Calculate remaining time in seconds
            remaining_time = expiry_timestamp - current_timestamp
            
            # Token is valid
            return Response({
                'success': True,
                'message': 'Token is valid',
                'expires_at': datetime.fromtimestamp(expiry_timestamp).isoformat(),
                'expires_in_seconds': int(remaining_time)
            }, status=status.HTTP_200_OK)
            
        except TokenError as e:
            return Response({
                'success': False,
                'message': f'Invalid token: {str(e)}'
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error validating token: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['price', 'created_at', 'name']
    filterset_fields = ['category', 'status', 'is_featured']
    pagination_class = PageNumberPagination
    authentication_classes = []
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Price range filtering
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        # Stock status filtering
        in_stock = self.request.query_params.get('in_stock')
        if in_stock is not None:
            if in_stock.lower() == 'true':
                queryset = queryset.filter(stock_quantity__gt=0)
            elif in_stock.lower() == 'false':
                queryset = queryset.filter(stock_quantity=0)
                
        return queryset

def format_phone_number(country_code, phone_number):
    """Format phone number with country code"""
    # Simple formatting - you can customize this
    return f"{country_code} {phone_number}"

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if not serializer.is_valid():
            # Format error messages nicely
            error_messages = self._format_error_messages(serializer.errors)
            return Response({
                'status': 'error',
                'success': False,  # Boolean indicator for failure
                'message': 'Validation error',
                'errors': error_messages
            }, status=status.HTTP_400_BAD_REQUEST)
            
        self.perform_update(serializer)
        return Response({
            'status': 'success',
            'success': True,  # Boolean indicator for success
            'message': 'Profile updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'])
    def upload_photo(self, request):
        try:
            profile = request.user.profile
            photo = request.FILES.get('photo')
            if not photo:
                return Response({
                    'status': 'error',
                    'success': False,  # Boolean indicator for failure
                    'message': 'No photo provided'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            profile.photo = photo
            profile.save()
            
            return Response({
                'status': 'success',
                'success': True,  # Boolean indicator for success
                'message': 'Photo uploaded successfully',
                'data': ProfileSerializer(profile, context={'request': request}).data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'success': False,  # Boolean indicator for failure
                'message': "Failed to upload photo"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['DELETE'])
    def remove_photo(self, request):
        try:
            profile = request.user.profile
            if profile.photo:
                profile.photo.delete()
                profile.save()
            
            return Response({
                'status': 'success',
                'success': True,  # Boolean indicator for success
                'message': 'Photo removed successfully'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'success': False,  # Boolean indicator for failure
                'message': "Failed to remove photo"
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['PATCH', 'PUT'], url_path='update-details')
    def update_details(self, request):
        """
        Endpoint to update the user's full name, email, photo, and phone number
        """
        try:
            profile = request.user.profile
            serializer = UserDetailsUpdateSerializer(
                profile, 
                data=request.data,
                context={'request': request},
                partial=True
            )
            
            if not serializer.is_valid():
                error_messages = self._format_error_messages(serializer.errors)
                return Response({
                    'status': 'error',
                    'success': False,
                    'message': 'Validation error',
                    'errors': error_messages
                }, status=status.HTTP_400_BAD_REQUEST)
            
            profile = serializer.save()
            
            # Format the phone number for the response
            formatted_phone = None
            if profile.phone_number and profile.country_code:
                formatted_phone = format_phone_number(profile.country_code, profile.phone_number)
            
            return Response({
                'status': 'success',
                'success': True,
                'message': 'User details updated successfully',
                'data': {
                    'full_name': profile.full_name,
                    'email': profile.user.email,
                    'photo_url': self.get_serializer(profile).get_photo_url(profile) if profile.photo else None,
                    'phone_number': profile.phone_number,
                    'country_code': profile.country_code,
                    'formatted_phone_number': formatted_phone
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            print(traceback.format_exc())  # This will help to debug by showing the full error in your console
            return Response({
                'status': 'error',
                'success': False,
                'message': f"Failed to update user details: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def _format_error_messages(self, errors):
        """Convert complex validation errors to simple messages"""
        formatted_errors = {}
        
        for field, error_list in errors.items():
            if isinstance(error_list, list):
                # Get first error message without technical details
                error_message = error_list[0]
                if hasattr(error_message, 'detail'):
                    formatted_errors[field] = error_message.detail
                else:
                    formatted_errors[field] = str(error_message)
            elif isinstance(error_list, dict):
                # Handle nested serializers
                formatted_errors[field] = self._format_error_messages(error_list)
            else:
                formatted_errors[field] = str(error_list)
                
        return formatted_errors

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # Format error messages nicely
            error_messages = self._format_error_messages(serializer.errors)
            return Response({
                'status': 'error',
                'success': False,  # Boolean indicator for failure
                'message': 'Validation error',
                'errors': error_messages
            }, status=status.HTTP_400_BAD_REQUEST)
            
        self.perform_create(serializer)
        return Response({
            'status': 'success',
            'success': True,  # Boolean indicator for success
            'message': 'Address added successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if not serializer.is_valid():
            # Format error messages nicely
            error_messages = self._format_error_messages(serializer.errors)
            return Response({
                'status': 'error',
                'success': False,  # Boolean indicator for failure
                'message': 'Validation error',
                'errors': error_messages
            }, status=status.HTTP_400_BAD_REQUEST)
            
        self.perform_update(serializer)
        return Response({
            'status': 'success',
            'success': True,  # Boolean indicator for success
            'message': 'Address updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                'status': 'success',
                'success': True,  # Boolean indicator for success
                'message': 'Address deleted successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'success': False,  # Boolean indicator for failure
                'message': "Failed to delete address"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['POST'])
    def set_default(self, request, pk=None):
        try:
            address = self.get_object()
            address.is_default = True
            address.save()
            return Response({
                'status': 'success',
                'success': True,  # Boolean indicator for success
                'message': 'Address set as default successfully'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'success': False,  # Boolean indicator for failure
                'message': "Failed to set address as default"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def _format_error_messages(self, errors):
        """Convert complex validation errors to simple messages"""
        formatted_errors = {}
        
        for field, error_list in errors.items():
            if isinstance(error_list, list):
                # Get first error message without technical details
                error_message = error_list[0]
                if hasattr(error_message, 'detail'):
                    formatted_errors[field] = error_message.detail
                else:
                    formatted_errors[field] = str(error_message)
            elif isinstance(error_list, dict):
                # Handle nested serializers
                formatted_errors[field] = self._format_error_messages(error_list)
            else:
                formatted_errors[field] = str(error_list)
                
        return formatted_errors
        
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # Changed from AllowAny to IsAuthenticated
    
    def get_queryset(self):
        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.save()
            session_key = self.request.session.session_key
            
        # If the user is authenticated, also check for user-linked carts
        if self.request.user.is_authenticated:
            return Cart.objects.filter(
                Q(session_key=session_key) | Q(user=self.request.user)
            ).prefetch_related('items')
        else:
            return Cart.objects.filter(session_key=session_key).prefetch_related('items')
    
    def get_serializer_class(self):
        if self.action in ['add_item', 'update_quantity']:
            return CartItemSerializer
        return CartSerializer

    def get_cart(self):
        """Get or create cart for current session and/or user"""
        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.save()
            session_key = self.request.session.session_key
        
        # If user is authenticated, try to find their cart
        if self.request.user.is_authenticated:
            # Try to get a cart tied to the user
            user_cart = Cart.objects.filter(user=self.request.user).first()
            
            # If no user cart, check for session cart
            session_cart = Cart.objects.filter(session_key=session_key).first()
            
            if user_cart:
                # If both user cart and session cart exist, merge them
                if session_cart and session_cart.id != user_cart.id:
                    # Transfer items from session cart to user cart
                    for item in session_cart.items.all():
                        # Check if this product already exists in user cart
                        existing_item = CartItem.objects.filter(
                            cart=user_cart, 
                            product=item.product
                        ).first()
                        
                        if existing_item:
                            # Update quantity of existing item
                            existing_item.quantity += item.quantity
                            existing_item.save()
                        else:
                            # Create new item in user cart
                            item.cart = user_cart
                            item.save()
                    
                    # Delete the session cart after merging
                    session_cart.delete()
                
                return user_cart
            elif session_cart:
                # Link the existing session cart to the user
                session_cart.user = self.request.user
                session_cart.save()
                return session_cart
            else:
                # Create a new cart for the user
                return Cart.objects.create(
                    user=self.request.user,
                    session_key=session_key
                )
        else:
            # For anonymous users, just use session
            cart, created = Cart.objects.get_or_create(session_key=session_key)
            return cart

    @action(detail=False, methods=['GET'])
    def summary(self, request):
        """Get cart summary with totals"""
        cart = self.get_cart()
        items = CartItem.objects.filter(cart=cart).select_related('product')
        
        subtotal = sum(item.product.price * item.quantity for item in items)
        shipping = Decimal('0.00')  # Can be calculated based on your logic
        
        # Calculate total quantity (sum of all item quantities)
        total_quantity = sum(item.quantity for item in items)
        
        return Response({
            'cart_id': cart.id,
            'items': CartItemSerializer(items, many=True).data,
            'subtotal': subtotal,
            'shipping': shipping,
            'total': subtotal + shipping,
            'item_count': items.count(), 
            'total_quantity': total_quantity  # New field for total quantity
        })

    @action(detail=False, methods=['POST'])
    def add_item(self, request):
        """Add item to cart"""
        cart = self.get_cart()
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))
        
        print(f"Adding to cart - Product ID: {product_id}, Quantity: {quantity}")
        print(f"Current cart: ID {cart.id}, Session: {cart.session_key}")
        
        try:
            product = Product.objects.get(id=product_id)
            
            # Update or create cart item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
                print(f"Updated cart item: {cart_item.id}, New quantity: {cart_item.quantity}")
            else:
                print(f"Created new cart item: {cart_item.id}, Quantity: {cart_item.quantity}")
            
            # Verify cart items after add
            items_after = list(CartItem.objects.filter(cart=cart).values('id', 'product__name', 'quantity'))
            print(f"Items in cart after add: {items_after}")
            
            # Return cart summary
            summary = {
                'cart_id': cart.id,
                'total_items': CartItem.objects.filter(cart=cart).count(),
                'item_added': CartItemSerializer(cart_item).data,
                'all_items': CartItemSerializer(CartItem.objects.filter(cart=cart), many=True).data
            }
            
            return Response(summary)
            
        except Product.DoesNotExist:
            print(f"Product with ID {product_id} not found")
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error adding item to cart: {str(e)}")
            return Response(
                {'error': f'Failed to add item to cart: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    @action(detail=False, methods=['POST'])
    def update_quantity(self, request):
        """Update item quantity in cart"""
        cart = self.get_cart()
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 0))
        
        try:
            cart_item = CartItem.objects.get(cart=cart, id=item_id)
            
            # Check stock availability
            if quantity > cart_item.product.stock_quantity:
                return Response(
                    {'error': 'Not enough stock available'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
            else:
                cart_item.delete()
                
            return Response({'status': 'success'})
            
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['POST'])
    def apply_discount(self, request):
        """Apply discount code to cart"""
        code = request.data.get('code')
        cart = self.get_cart()
        
        # Implement your discount logic here
        # For now returning a mock response
        return Response({
            'status': 'success',
            'discount': '10.00',
            'message': 'Discount applied successfully'
        })

    @action(detail=False, methods=['POST'])
    def remove_item(self, request):
        """Remove item from cart"""
        cart = self.get_cart()
        item_id = request.data.get('item_id')
        
        try:
            cart_item = CartItem.objects.get(cart=cart, id=item_id)
            cart_item.delete()
            return Response({'status': 'success'})
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['POST'])
    def clear(self, request):
        """Clear all items from cart"""
        cart = self.get_cart()
        CartItem.objects.filter(cart=cart).delete()
        return Response({'status': 'success'})
    
class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]  #Changed from AllowAny to IsAuthenticated

    def get_queryset(self):
        cart = self.get_cart()
        return CartItem.objects.filter(cart=cart)

    def get_cart(self):
        """Get or create cart for current session and/or user"""
        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.save()
            session_key = self.request.session.session_key
        
        # If user is authenticated, try to find their cart
        if self.request.user.is_authenticated:
            # Try to get a cart tied to the user
            user_cart = Cart.objects.filter(user=self.request.user).first()
            
            # If no user cart, check for session cart
            session_cart = Cart.objects.filter(session_key=session_key).first()
            
            if user_cart:
                # If both user cart and session cart exist, merge them
                if session_cart and session_cart.id != user_cart.id:
                    # Transfer items from session cart to user cart
                    for item in session_cart.items.all():
                        # Check if this product already exists in user cart
                        existing_item = CartItem.objects.filter(
                            cart=user_cart, 
                            product=item.product
                        ).first()
                        
                        if existing_item:
                            # Update quantity of existing item
                            existing_item.quantity += item.quantity
                            existing_item.save()
                        else:
                            # Create new item in user cart
                            item.cart = user_cart
                            item.save()
                    
                    # Delete the session cart after merging
                    session_cart.delete()
                
                return user_cart
            elif session_cart:
                # Link the existing session cart to the user
                session_cart.user = self.request.user
                session_cart.save()
                return session_cart
            else:
                # Create a new cart for the user
                return Cart.objects.create(
                    user=self.request.user,
                    session_key=session_key
                )
        else:
            # For anonymous users, just use session
            cart, created = Cart.objects.get_or_create(session_key=session_key)
            return cart
    
    def perform_create(self, serializer):
        cart = self.get_cart()
        serializer.save(cart=cart)

    @action(detail=False, methods=['GET'])
    def debug_info(self, request):
        """Get debug information about the current cart state"""
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key
            
        cart = self.get_cart()
        
        items = [
            {
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'quantity': item.quantity
            }
            for item in CartItem.objects.filter(cart=cart)
        ]
        
        debug_data = {
            'session_key': session_key,
            'cart': {
                'id': cart.id,
                'items_count': len(items),
                'items': items
            }
        }
        
        return Response(debug_data)
    
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related('user', 'customer').prefetch_related('items__product', 'payments')
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order_number', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'total', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    @action(detail=False, methods=['GET'])
    def customers(self, request):
        """Get list of customers for dropdown"""
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def add_item(self, request, pk=None):
        """Add item to existing order"""
        order = self.get_object()
        item_data = request.data
        item_data['order'] = order.id
        
        item_serializer = OrderItemSerializer(data=item_data)
        if item_serializer.is_valid():
            item_serializer.save()
            return Response(item_serializer.data)
        return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def bulk_action(self, request):
        order_ids = request.data.get('order_ids', [])
        action_type = request.data.get('action')
        
        if not order_ids or not action_type:
            return Response({
                'error': 'order_ids and action are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        orders = Order.objects.filter(id__in=order_ids)
        
        if action_type == 'update_status':
            new_status = request.data.get('status')
            if not new_status:
                return Response({
                    'error': 'status is required for update_status action'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            orders.update(status=new_status)
            
        elif action_type == 'delete':
            orders.delete()
            
        return Response({'status': 'success', 'processed': len(order_ids)})

    @action(detail=False, methods=['GET'])
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="orders-{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Order ID', 'Date', 'Customer', 'Email', 'Items', 
            'Total', 'Status', 'Payment Method', 'Payment Status'
        ])
        
        for order in queryset:
            items_str = ', '.join([
                f"{item.product.name} (x{item.quantity})"
                for item in order.items.all()
            ])
            
            writer.writerow([
                order.order_number,
                order.created_at.strftime('%Y-%m-%d %H:%M'),
                order.get_customer_name(),
                order.user.email,
                items_str,
                order.total,
                order.get_status_display(),
                order.payments.first().payment_method if order.payments.exists() else 'N/A',
                order.payments.first().status if order.payments.exists() else 'N/A'
            ])
        
        return response

    @action(detail=False, methods=['GET'])
    def summary(self, request):
        queryset = self.get_queryset()
        today = timezone.now().date()
        
        # Status summary
        status_summary = queryset.values('status').annotate(
            count=Count('id'),
            total_value=Sum('total')
        )
        
        # Today's orders
        today_orders = queryset.filter(
            created_at__date=today
        ).aggregate(
            count=Count('id'),
            total_value=Sum('total')
        )
        
        # Payment method distribution
        payment_methods = queryset.values(
            'payments__payment_method'  # or 'payments__method' depending on which field you want to use
        ).annotate(
            count=Count('id'),
            total_value=Sum('total')
        )
        
        return Response({
            'status_summary': status_summary,
            'today_summary': today_orders,
            'payment_methods': payment_methods
        })

    @action(detail=True, methods=['POST'])
    def add_note(self, request, pk=None):
        order = self.get_object()
        note_content = request.data.get('note')
        
        if not note_content:
            return Response({
                'error': 'Note content is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if order.note:  # Changed from notes to note
            order.note += f"\n[{timezone.now().strftime('%Y-%m-%d %H:%M')}] {note_content}"
        else:
            order.note = f"[{timezone.now().strftime('%Y-%m-%d %H:%M')}] {note_content}"
        
        order.save()
        return Response({'status': 'success'})

    @action(detail=True, methods=['POST'])
    def update_payment(self, request, pk=None):
        order = self.get_object()
        payment_status = request.data.get('status')
        transaction_id = request.data.get('transaction_id')
        
        if not payment_status:
            return Response({
                'error': 'Payment status is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        payment = order.payments.first()
        if not payment:
            return Response({
                'error': 'No payment found for this order'
            }, status=status.HTTP_404_NOT_FOUND)
        payment.status = payment_status
        
        order.payment.status = payment_status
        if transaction_id:
            order.payment.transaction_id = transaction_id
        order.payment.save()
        
        return Response({'status': 'success'})      
    @action(detail=False, methods=['POST'])
    def create_order(self, request):
        """Create a new order with items"""
        # Validate order data
        order_serializer = OrderCreateSerializer(data=request.data)
        if not order_serializer.is_valid():
            return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create order
        order = order_serializer.save()

        # Add items to order
        items_data = request.data.get('items', [])
        for item_data in items_data:
            item_data['order'] = order.id
            item_serializer = OrderItemSerializer(data=item_data)
            if item_serializer.is_valid():
                item_serializer.save()
            else:
                order.delete()
                return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST'])
    def update_status(self, request, pk=None):
        """Update order status"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data)  
    
# Product Search and Filtering Views
class ProductSearchView(generics.ListAPIView):
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'description', 'sku', 'tags__name', 'category__name']
    filterset_fields = ['category', 'tags', 'is_featured', 'status']
    
    def get_queryset(self):
        Product = apps.get_model('api', 'Product')
        queryset = Product.objects.filter(status='active')
        
        # Additional filtering logic
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        
        if price_min:
            queryset = queryset.filter(price__gte=float(price_min))
        if price_max:
            queryset = queryset.filter(price__lte=float(price_max))
            
        # Record user view if a single product is being viewed
        product_id = self.request.query_params.get('product_id')
        if product_id and self.request.user.is_authenticated:
            try:
                product = Product.objects.get(id=product_id)
                ProductView = apps.get_model('api', 'ProductView')
                ProductView.objects.create(
                    product=product,
                    user=self.request.user,
                    viewed_at=timezone.now()
                )
            except Product.DoesNotExist:
                pass
                
        return queryset
        

# Wishlist Views
class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return Wishlist objects, not WishlistItem objects
        return Wishlist.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            # Get the correct product count
            wishlist = Wishlist.objects.filter(user=request.user).first()
            if wishlist:
                # Get unique product IDs using similar logic as in the serializer
                wishlist_items = wishlist.items.all().select_related('product')
                unique_product_ids = set(item.product.id for item in wishlist_items)
                
                # Update the existing count with the correct number
                response.data['count'] = len(unique_product_ids)
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # Get or create the user's wishlist
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        
        # Check for duplicate products before saving
        product_id = self.request.data.get('product')
        if product_id:
            # Check if the product already exists in the wishlist
            existing_item = WishlistItem.objects.filter(
                wishlist=wishlist, 
                product_id=product_id
            ).first()
            
            # If the item already exists, raise a validation error
            if existing_item:
                raise serializers.ValidationError({
                    "error": "Product already exists in your wishlist"
                })
        
        serializer.save(wishlist=wishlist)
    
    
    @action(detail=False, methods=['POST'], url_path='move-to-cart/(?P<pk>[^/.]+)')
    def move_to_cart(self, request, pk=None):
        """Move a single item from wishlist to cart using product_id"""
        try:
            # Find the wishlist item by product_id instead of item_id
            product_id = pk  # Use pk as the product_id
            wishlist_item = WishlistItem.objects.filter(
                wishlist__user=request.user,
                product_id=product_id
            ).first()
            
            if not wishlist_item:
                return Response(
                    {'error': 'Product not found in your wishlist'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
                # Get cart using the CartViewSet's get_cart method
            cart_viewset = CartViewSet()
            cart_viewset.request = request
            cart = cart_viewset.get_cart()
            
            if wishlist_item.product.stock_quantity > 0:
                # Create or update cart item
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=wishlist_item.product,
                    defaults={'quantity': 1}
                )
                
                # If cart item already existed, increment quantity
                if not created:
                    cart_item.quantity += 1
                    cart_item.save()
                    
                wishlist_item.delete()
                return Response({'status': 'Item moved to cart successfully'})
            else:
                return Response(
                    {'warning': 'Item is out of stock and cannot be added to cart'},
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )        
    @action(detail=False, methods=['POST'])
    def bulk_delete(self, request):
        """Delete multiple wishlist items at once using product IDs"""
        try:
            product_ids = request.data.get('product_ids', [])  # Changed from item_ids to product_ids
            WishlistItem.objects.filter(
                wishlist__user=request.user,
                product_id__in=product_ids
            ).delete()
            return Response({'status': 'Items deleted successfully'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['GET'])
    def stock_notifications(self, request):
        """Get stock notifications for wishlist items"""
        wishlist_items = WishlistItem.objects.filter(
            wishlist__user=request.user
        ).select_related('product')
        
        notifications = []
        for item in wishlist_items:
            if item.product.stock_quantity > 0:
                # Get main image URL
                main_image = None
                if hasattr(item.product, 'main_image') and item.product.main_image:
                    main_image = item.product.main_image.url
                elif hasattr(item.product, 'images') and item.product.images and len(item.product.images) > 0:
                    main_image = item.product.images[0]
                    
                # Create consistent notification object with all fields
                notification = {
                    'product_id': item.product.id,
                    'product_name': item.product.name,
                    'stock_quantity': item.product.stock_quantity,
                    'added_at': item.added_at.isoformat(),
                    'is_liked': True  # Add this field to show the item is liked/wishlisted
                }
                
                # Add optional fields if they exist on the product model
                if hasattr(item.product, 'description'):
                    notification['product_description'] = item.product.description
                
                if main_image:
                    notification['main_image'] = main_image
                
                if hasattr(item.product, 'images') and item.product.images:
                    notification['images'] = item.product.images
                
                if hasattr(item.product, 'price'):
                    notification['price'] = str(item.product.price)  # Convert to string to ensure it's JSON serializable
                
                notifications.append(notification)
        
        return Response(notifications)

class WishlistItemViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WishlistItem.objects.filter(wishlist__user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Get or create the user's wishlist
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        
        # Get the product ID from the request
        product_id = request.data.get('product')
        
        # Validate product exists
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if the product is already in the wishlist
        existing_item = WishlistItem.objects.filter(
            wishlist=wishlist, 
            product_id=product_id
        ).first()
        
        # If the item already exists, return an error
        if existing_item:
            return Response(
                {'error': 'Product already exists in your wishlist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare data for serializer
        mutable_data = {
            'wishlist': wishlist.id,
            'product': product_id
        }
        
        # Create new wishlist item
        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            {'message': 'Product added to wishlist', 'data': serializer.data},
            status=status.HTTP_201_CREATED, 
            headers=headers
        )
    
    def perform_create(self, serializer):
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        serializer.save(wishlist=wishlist)

    @action(detail=True, methods=['DELETE'])
    def remove_item(self, request, pk=None):
        """Remove a single item from the wishlist"""
        try:
            wishlist_item = WishlistItem.objects.get(
                id=pk,
                wishlist__user=request.user
            )
            wishlist_item.delete()
            return Response({
                'status': 'Item removed from wishlist successfully'
            }, status=status.HTTP_200_OK)
        except WishlistItem.DoesNotExist:
            return Response({
                'error': 'Item not found in your wishlist'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['DELETE'])
    def remove_by_product_id(self, request, product_id=None):
        """Remove wishlist item by product_id rather than item_id"""
        try:
            # Find the wishlist item by product_id instead of item_id
            wishlist_item = WishlistItem.objects.filter(
                wishlist__user=request.user,
                product_id=product_id
            ).first()
            
            if not wishlist_item:
                return Response({
                    'error': 'Product not found in your wishlist'
                }, status=status.HTTP_404_NOT_FOUND)
                
            wishlist_item.delete()
            return Response({
                'status': 'Item removed from wishlist successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=False, methods=['POST'])
    def bulk_delete(self, request):
        """Delete multiple wishlist items at once using product IDs"""
        try:
            product_ids = request.data.get('product_ids', [])  # Changed from item_ids to product_ids
            WishlistItem.objects.filter(
                wishlist__user=request.user,
                product_id__in=product_ids
            ).delete()
            return Response({'status': 'Items deleted successfully'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """Delete a single wishlist item"""
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                'status': 'Item removed from wishlist successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

# Product Recommendation View
class ProductRecommendationView(generics.ListAPIView):
    serializer_class = ProductRecommendationSerializer
    
    def get_immediate_recommendations(self, product=None, limit=4):
        """Get any active products as a last resort fallback"""
        Product = apps.get_model('api', 'Product')
        queryset = Product.objects.filter(status='active')
        
        # If we have a product, exclude it from results
        if product:
            queryset = queryset.exclude(id=product.id)
            
        # Order by something sensible
        queryset = queryset.order_by('-is_featured', '-created_at')[:limit]
        
        # If we still don't have results, just get any products
        if not queryset.exists():
            queryset = Product.objects.all().order_by('-id')[:limit]
            
        return queryset
    
    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        rec_type = self.request.query_params.get('type', 'similar')
        Product = apps.get_model('api', 'Product')
        
        try:
            # Try to get the product
            product = Product.objects.get(id=product_id)
            recommendations = []
            
            # Logic for different recommendation types
            if rec_type == 'similar':
                # Get products in same category
                recommendations = Product.objects.filter(
                    category=product.category,
                    status='active'
                ).exclude(id=product.id)
                
            elif rec_type == 'complementary':
                # Get complementary products if possible
                if hasattr(product, 'get_complementary_products'):
                    recommendations = product.get_complementary_products()
                
                # If no results, try products with different price points
                if not recommendations.exists():
                    recommendations = Product.objects.filter(
                        status='active'
                    ).exclude(id=product.id).order_by('?')
                
            elif rec_type == 'personalized':
                # Just get featured products for now
                recommendations = Product.objects.filter(
                    status='active',
                    is_featured=True
                ).exclude(id=product.id)
            
            # If we still don't have recommendations, get any active products
            if not recommendations.exists():
                recommendations = self.get_immediate_recommendations(product)
                
            # Make sure we limit the results
            return recommendations[:4]
            
        except Product.DoesNotExist:
            # If product doesn't exist, return any active products
            return self.get_immediate_recommendations(product=None)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        response_data = {
            'status': 'success',
            'count': len(serializer.data),
            'recommendations': serializer.data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

# Add this view to track product views
class RecordProductViewView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        Product = apps.get_model('api', 'Product')
        ProductView = apps.get_model('api', 'ProductView')
        
        product_id = request.data.get('product_id')
        
        try:
            product = Product.objects.get(id=product_id)
            
            if request.user.is_authenticated:
                ProductView.objects.create(
                    product=product,
                    user=request.user,
                    viewed_at=timezone.now()
                )
                
                return Response({
                    'status': 'success',
                    'message': 'Product view recorded'
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'status': 'error',
                    'message': 'User not authenticated'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except Product.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
class ReviewFilter(django_filters.FilterSet):
    rating = django_filters.NumberFilter()
    has_images = django_filters.BooleanFilter(method='filter_has_images')
    tag = django_filters.CharFilter(field_name='tags__slug')
    
    class Meta:
        model = Review
        fields = ['rating', 'has_images', 'tag']
    
    def filter_has_images(self, queryset, name, value):
        if value:
            return queryset.exclude(images=[])
        return queryset

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [django_filters.DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['created_at', 'helpful_votes', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        return Review.objects.all()

    def perform_create(self, serializer):
        # Check if user has purchased the product
        product = serializer.validated_data['product']
        user = self.request.user
        is_verified = OrderItem.objects.filter(
            order__user=user,
            product=product,
            order__status='DELIVERED'
        ).exists()
        
        serializer.save(
            user=user,
            is_verified_purchase=is_verified
        )

    @action(detail=True, methods=['POST'])
    def helpful(self, request, pk=None):
        review = self.get_object()
        user = request.user
        
        vote, created = ReviewHelpfulVote.objects.get_or_create(
            review=review,
            user=user
        )
        
        if not created:
            # User is un-marking as helpful
            vote.delete()
            review.helpful_votes = ReviewHelpfulVote.objects.filter(review=review).count()
            review.save()
            return Response({'helpful': False, 'count': review.helpful_votes})
            
        review.helpful_votes = ReviewHelpfulVote.objects.filter(review=review).count()
        review.save()
        return Response({'helpful': True, 'count': review.helpful_votes})

    @action(detail=False, methods=['GET'])
    def summary(self, request):
        product_id = request.query_params.get('product')
        if not product_id:
            return Response(
                {'error': 'Product ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        review = Review.objects.filter(product_id=product_id).first()
        if not review:
            return Response({
                'rating_distribution': {i: 0 for i in range(1, 6)},
                'tag_distribution': {}
            })
            
        serializer = ReviewSummarySerializer(review)
        return Response(serializer.data)
    
class CheckoutViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['GET'])
    def payment_methods(self, request):
        """Return available payment methods"""
        return Response({
            'methods': [
                {
                    'id': 'visa',
                    'name': 'Visa',
                    'enabled': True
                },
                {
                    'id': 'mastercard',
                    'name': 'Mastercard',
                    'enabled': True
                },
                {
                    'id': 'stripe',
                    'name': 'Stripe',
                    'enabled': True
                },
                {
                    'id': 'paypal',
                    'name': 'PayPal',
                    'enabled': True
                },
                {
                    'id': 'google_pay',
                    'name': 'Google Pay',
                    'enabled': True
                },
                {
                    'id': 'clover',
                    'name': 'Clover',
                    'enabled': True
                }
            ]
        })
    
    @action(detail=False, methods=['POST'])
    def validate_promocode(self, request):
        """Validate promocode and return discount amount"""
        promocode = request.data.get('promocode')
        subtotal = Decimal(request.data.get('subtotal', '0'))

        try:
            discount = self._calculate_discount(promocode, subtotal)
            return Response({
                'valid': True,
                'discount_percentage': 20,  # Example fixed percentage
                'discount_amount': discount
            })
        except ValueError as e:
            return Response({
                'valid': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def process(self, request):
        """Process checkout"""
        try:
            with transaction.atomic():
                # Get cart and items
                cart = Cart.objects.get(user=request.user)
                cart_items = CartItem.objects.filter(cart=cart).select_related('product')
                
                if not cart_items.exists():
                    return Response({
                        'status': 'error',
                        'message': 'Cart is empty'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validate address (using new method)
                address_data = request.data.get('address')
                self.validate_shipping_address(address_data)

                # Validate stock (using new method)
                self.validate_stock(cart_items)

                # Calculate totals (using new method)
                shipping_cost = Decimal('4.99')  # From your UI
                discount_code = request.data.get('discount_code')
                totals = self.calculate_order_totals(cart_items, shipping_cost, discount_code)

                # Create order with calculated totals
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=address_data['street_address'],
                    shipping_city=address_data['city'],
                    shipping_state=address_data['state'],
                    shipping_country=address_data['country'],
                    shipping_zip=address_data['zip_code'],
                    shipping_cost=shipping_cost,
                    subtotal=totals['subtotal'],
                    discount=totals['discount'],
                    total=totals['total'],
                    status='PENDING'
                )
                # Process order items
                for cart_item in cart_items:
                    if cart_item.quantity > cart_item.product.stock_quantity:
                        raise ValueError(f'Insufficient stock for {cart_item.product.name}')
                    
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price
                    )
                    
                    cart_item.product.stock_quantity -= cart_item.quantity
                    cart_item.product.save()
                    
                    subtotal += cart_item.product.price * cart_item.quantity

                # Apply discount
                discount_code = request.data.get('discount_code')
                discount_amount = Decimal('0.00')
                if discount_code:
                    discount_amount = self._calculate_discount(discount_code, subtotal)

                # Update order totals
                order.subtotal = subtotal
                order.discount = discount_amount
                order.total = subtotal - discount_amount + shipping_cost
                order.save()

                # Clear cart
                cart_items.delete()

                return Response({
                    'status': 'success',
                    'message': 'Order created successfully',
                    'order_id': order.id,
                    'total': order.total
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def process_payment(self, request):
        """Process payment for an order"""
        payment_method = request.data.get('payment_method')
        payment_data = request.data.get('payment_data')
        order_id = request.data.get('order_id')
        save_card = request.data.get('save_card', False)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
            
            payment_service = self._get_payment_service(payment_method)
            if not payment_service:
                return Response({
                    'status': 'error',
                    'message': 'Invalid payment method'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            result = payment_service.process_payment(order, payment_data)
            
            if result['success']:
                payment = Payment.objects.create(
                    order=order,
                    amount=order.total,
                    payment_method=payment_method,
                    transaction_id=result['transaction_id'],
                    status='COMPLETED',
                    gateway_response=result['response'],
                    save_card=save_card
                )
                
                if payment_data.get('card_details'):
                    payment.card_last_four = payment_data['card_details'].get('last4')
                    payment.card_brand = payment_data['card_details'].get('brand')
                    payment.card_expiry = payment_data['card_details'].get('exp_date')
                    payment.save()
                
                order.status = 'PAID'
                order.save()
                
                return Response({
                    'status': 'success',
                    'payment_id': payment.id
                })
            
            return Response({
                'status': 'error',
                'message': result['error']
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Order.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['GET'])
    def saved_payment_methods(self, request):
        """Get saved payment methods for the current user"""
        if not request.user.is_authenticated:
            return Response([], status=status.HTTP_200_OK)
            
        saved_methods = SavedPaymentMethod.objects.filter(user=request.user)
        return Response([
            {
                'id': method.id,
                'type': method.payment_type,
                'last_four': method.card_last_four,
                'brand': method.card_brand,
                'is_default': method.is_default
            }
            for method in saved_methods
        ])

    def _get_payment_service(self, payment_method):
        """Get appropriate payment service based on payment method"""
        services = {
            'STRIPE': StripePaymentService(),
            'PAYPAL': PayPalPaymentService(),
            'GOOGLE_PAY': GooglePayService(),
            'VISA': StripePaymentService(),
            'MASTERCARD': StripePaymentService(),
            'CLOVER': CloverPaymentService(),
        }
        return services.get(payment_method.upper())

    def _calculate_discount(self, promocode, subtotal):
        """Calculate discount amount based on promocode"""
        # Implement your discount logic here
        if not promocode:
            return Decimal('0.00')
            
        # Example: 20% discount
        return subtotal * Decimal('0.20')
    def validate_shipping_address(self, address_data):
        """
        Validates shipping address shown in the first screen
        """
        required_fields = ['street_address', 'city', 'state', 'zip_code', 'country']
        for field in required_fields:
            if not address_data.get(field):
                raise ValidationError(f'{field} is required')
        return True

    def calculate_order_totals(self, items, shipping_cost, discount_code=None):
        """
        Calculates totals shown in the Summary section
        """
        subtotal = sum(item.quantity * item.product.price for item in items)
        discount = self._calculate_discount(discount_code, subtotal) if discount_code else 0
        total = subtotal + shipping_cost - discount
        return {
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'discount': discount,
            'total': total
        }

    def validate_stock(self, cart_items):
        """
        Validates stock before proceeding to checkout
        """
        for item in cart_items:
            if item.quantity > item.product.stock_quantity:
                raise ValidationError(f'Insufficient stock for {item.product.name}')
        return True

    @action(detail=False, methods=['GET'])
    def get_client_secret(self, request):
        """Get Stripe client secret for frontend payment flow"""
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            intent = stripe.PaymentIntent.create(
                amount=int(float(request.GET.get('amount')) * 100),
                currency='usd'
            )
            return Response({'client_secret': intent.client_secret})
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['POST'])
    def create_clover_token(self, request):
        """Create a payment token from Clover for future use"""
        try:
            card_data = request.data.get('card_data', {})
            
            if not card_data:
                return Response({
                    'status': 'error',
                    'message': 'Card data is required'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            clover_service = CloverPaymentService()
            result = clover_service.get_payment_token(card_data)
            
            if result['success']:
                # If user is authenticated, you could save this token
                if request.user.is_authenticated and request.data.get('save_card', False):
                    SavedPaymentMethod.objects.create(
                        user=request.user,
                        payment_type='CLOVER',
                        token=result['token'],
                        card_last_four=result.get('card_last_four', ''),
                        card_brand=result.get('card_brand', ''),
                        is_default=not SavedPaymentMethod.objects.filter(user=request.user).exists()
                    )
                    
                return Response({
                    'status': 'success',
                    'token': result['token']
                })
                
            return Response({
                'status': 'error',
                'message': result.get('error', 'Failed to create payment token')
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['POST'])
    def shipping_cost(self, request):
        """Calculate shipping cost based on method and address"""
        shipping_method_id = request.data.get('shipping_method_id')
        address_id = request.data.get('address_id')
        
        try:
            shipping_method = ShippingMethod.objects.get(id=shipping_method_id)
            address = Address.objects.get(id=address_id, user=request.user)
            
            # You can implement custom shipping logic based on address
            shipping_cost = shipping_method.price
            
            return Response({
                'shipping_cost': shipping_cost,
                'estimated_days': shipping_method.estimated_days
            })
        except (ShippingMethod.DoesNotExist, Address.DoesNotExist):
            return Response({
                'error': 'Invalid shipping method or address'
            }, status=status.HTTP_400_BAD_REQUEST)
        
class ShippingMethodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ShippingMethod.objects.filter(is_active=True)
    serializer_class = ShippingMethodSerializer
    permission_classes = [IsAuthenticated]


class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return SupportTicket.objects.filter(user=user)
        return SupportTicket.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_authenticated:
            serializer.save(user=user)
        else:
            serializer.save()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return success message
        return Response({
            'status': 'success',
            'message': 'We have received your message, and we\'ll get back to you.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['GET'])
    def cart_metrics(self, request):
        """Get abandoned cart rate and related metrics"""
        time_period = request.query_params.get('period', 'week')
        date_threshold = self._get_date_threshold(time_period)
        
        total_carts = Cart.objects.filter(
            created_at__gte=date_threshold
        ).count()
        
        abandoned_carts = Cart.objects.filter(
            created_at__gte=date_threshold,
            items__isnull=False
        ).exclude(
            user__orders__created_at__gte=F('created_at')
        ).distinct().count()
        
        abandoned_rate = (abandoned_carts / total_carts * 100) if total_carts > 0 else 0
        
        data = {
            'abandoned_rate': round(abandoned_rate, 2),
            'total_carts': total_carts,
            'abandoned_carts': abandoned_carts,
            'period': time_period
        }
        
        serializer = DashboardCartMetricsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def customer_metrics(self, request):
        """Get customer-related metrics"""
        time_period = request.query_params.get('period', 'week')
        date_threshold = self._get_date_threshold(time_period)
        
        total_customers = CustomUser.objects.count()
        active_customers = CustomUser.objects.filter(
            orders__created_at__gte=date_threshold
        ).distinct().count()
        
        previous_customers = CustomUser.objects.filter(
            date_joined__lt=date_threshold
        ).count()
        
        growth_rate = ((total_customers - previous_customers) / previous_customers * 100) if previous_customers > 0 else 0
        
        data = {
            'total_customers': total_customers,
            'active_customers': active_customers,
            'growth_rate': round(growth_rate, 2),
            'period': time_period
        }
        
        serializer = DashboardCustomerMetricsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def order_metrics(self, request):
        """Get order-related metrics"""
        time_period = request.query_params.get('period', 'week')
        date_threshold = self._get_date_threshold(time_period)
        
        orders = Order.objects.filter(created_at__gte=date_threshold)
        orders_by_status = orders.values('status').annotate(
            count=Count('id')
        )
        
        order_totals = orders.aggregate(
            total_revenue=Sum('total'),
            total_orders=Count('id')
        )
        
        data = {
            'orders_by_status': orders_by_status,
            'total_revenue': order_totals['total_revenue'] or 0,
            'total_orders': order_totals['total_orders'],
            'period': time_period
        }
        
        serializer = DashboardOrderMetricsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def sales_trend(self, request):
        """Get sales trend data"""
        time_period = request.query_params.get('period', 'week')
        date_threshold = self._get_date_threshold(time_period)
        
        sales_data = Order.objects.filter(
            created_at__gte=date_threshold,
            status__in=['PROCESSING', 'SHIPPED', 'DELIVERED']
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            revenue=Sum('total'),
            orders=Count('id')
        ).order_by('date')
        
        serializer = DashboardSalesTrendSerializer(sales_data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def recent_orders(self, request):
        """Get recent orders with details"""
        orders = Order.objects.select_related('user').prefetch_related(
            'items__product'
        ).order_by('-created_at')[:10]
        
        orders_data = []
        for order in orders:
            order_data = {
                'id': order.id,
                'user_email': order.user.email,
                'total': order.total,
                'status': order.status,
                'created_at': order.created_at,
                'items': [
                    {
                        'product_name': item.product.name,
                        'quantity': item.quantity,
                        'price': item.price
                    } for item in order.items.all()
                ]
            }
            orders_data.append(order_data)
        
        serializer = DashboardRecentOrderSerializer(orders_data, many=True)
        return Response(serializer.data)

    def _get_date_threshold(self, period):
        """Helper method to get date threshold based on period"""
        now = timezone.now()
        thresholds = {
            'day': now - timedelta(days=1),
            'week': now - timedelta(weeks=1),
            'month': now - timedelta(days=30),
            'year': now - timedelta(days=365)
        }
        return thresholds.get(period, thresholds['week'])

class ProductFilter(django_filters.FilterSet):
    tab = django_filters.CharFilter(method='filter_tab')
    search = django_filters.CharFilter(method='filter_search')
    category = django_filters.CharFilter(method='filter_category')
    
    class Meta:
        model = Product
        fields = ['tab', 'search', 'category']

    def filter_tab(self, queryset, name, value):
        if value == 'all':
            return queryset
        elif value == 'published':
            return queryset.filter(status='published')
        elif value == 'low_stock':
            return queryset.filter(stock_quantity__lte=10)  # Threshold is adjustable 
        elif value == 'draft':
            return queryset.filter(status='draft')
        return queryset
    
    def filter_category(self, queryset, name, value):
        """
        Filter products by either category name or slug
        """
        # First try by slug (preferred for URLs)
        category_by_slug = queryset.filter(category__slug__iexact=value)
        if category_by_slug.exists():
            return category_by_slug
            
        # If no results by slug, try by name
        return queryset.filter(category__name__iexact=value)


    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(sku__icontains=value)
        )
# Update the ProductViewSet
from django.db import models
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    permission_classes = [IsAdminUser]  # Only admin users can manage sizes

class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [IsAdminUser]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductManagementSerializer
    filterset_class = ProductFilter
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    authentication_classes = [JWTAuthentication, TokenAuthentication, SessionAuthentication]  # Add authentication
    permission_classes = [AllowAny]  # Allow anyone to view products but the auth context will be used for wishlist
    search_fields = ['name', 'description', 'category__name']
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        queryset = Product.objects.prefetch_related(
            'variations',
            
        )
        
        # If user is authenticated, prefetch wishlist data
        if self.request.user.is_authenticated:
            # This will help optimize the wishlist queries
            user_wishlist_products = WishlistItem.objects.filter(
                wishlist__user=self.request.user
            ).values_list('product_id', flat=True)
            
            # You can add the wishlist info to the queryset
            # This allows you to optimize the is_liked check in serializer
            queryset = queryset.annotate(
                is_in_wishlist=models.Exists(
                    WishlistItem.objects.filter(
                        wishlist__user=self.request.user,
                        product_id=models.OuterRef('pk')
                    )
                )
            )
        
        return queryset
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve'] and self.request.query_params.get('view') == 'management':
            return ProductManagementSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Make sure we include the request in the context
        context['request'] = self.request
        return context

    def list(self, request, *args, **kwargs):
        # Apply filters
        queryset = self.filter_queryset(self.get_queryset())
        
        # Compute tab counts
        tab_counts = {
            'all': Product.objects.count(),
            'published': Product.objects.filter(status='published').count(),
            'low_stock': Product.objects.filter(stock_quantity__lte=10).count(),
            'draft': Product.objects.filter(status='draft').count()
        }
        
        # Paginate and serialize
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['tab_counts'] = tab_counts
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'tab_counts': tab_counts
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        # Get filtered queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Product ID', 
            'Product Name', 
            'SKU', 
            'Category', 
            'Stock Quantity', 
            'Price', 
            'Status', 
            'Added Date'
        ])
        
        for product in queryset:
            writer.writerow([
                product.id,
                product.name,
                product.sku,
                product.category.name if product.category else 'N/A',
                product.stock_quantity,
                str(product.price),
                product.get_status_display(),
                product.created_at.strftime('%d %b %Y')
            ])
        
        return response

    
    @action(detail=False, methods=['post'])
    def bulk_update_status(self, request):
        product_ids = request.data.get('product_ids', [])
        new_status = request.data.get('status')
        
        if not new_status or not product_ids:
            return Response({
                'error': 'Missing required parameters',
                'details': {
                    'product_ids': 'List of product IDs is required',
                    'status': 'New status is required'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate status
        valid_statuses = [choice[0] for choice in Product.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response({
                'error': 'Invalid status',
                'valid_statuses': valid_statuses
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Perform bulk update
        updated_count = Product.objects.filter(id__in=product_ids).update(status=new_status)
        
        return Response({
            'status': 'success',
            'updated_count': updated_count,
            'total_requested': len(product_ids)
        })

    @action(detail=False, methods=['get'])
    def tab_counts(self, request):
        """
        Endpoint to get product counts for each tab
        """
        return Response({
            'all': Product.objects.count(),
            'published': Product.objects.filter(status='published').count(),
            'low_stock': Product.objects.filter(stock_quantity__lte=10).count(),
            'draft': Product.objects.filter(status='draft').count()
        })

    @action(detail=True, methods=['PATCH'])
    def update_status(self, request, pk=None):
        """
        Update status for a single product
        """
        product = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response({
                'error': 'Status is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        valid_statuses = [choice[0] for choice in Product.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response({
                'error': 'Invalid status',
                'valid_statuses': valid_statuses
            }, status=status.HTTP_400_BAD_REQUEST)
        
        product.status = new_status
        product.save()
        
        serializer = self.get_serializer(product)
        return Response(serializer.data)
    def create(self, request, *args, **kwargs):
        # Handle variations during product creation
        variations_data = request.data.pop('variations', [])
        
        # Create product
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        
        # Create variations
        for variation_data in variations_data:
            ProductVariation.objects.create(
                product=product,
                variation_type=variation_data.get('variation_type'),
                variation_value=variation_data.get('variation_value')
            )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # Similar to create, but for updating
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Handle variations
        variations_data = request.data.pop('variations', [])
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        
        # Update variations
        # This is a simple approach - you might want more sophisticated variation management
        product.variations.all().delete()
        for variation_data in variations_data:
            ProductVariation.objects.create(
                product=product,
                variation_type=variation_data.get('variation_type'),
                variation_value=variation_data.get('variation_value')
            )
        
        return Response(serializer.data)
    @action(detail=True, methods=['POST'], url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Handle image uploads for products"""
        product = self.get_object()
        
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No image file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        image = request.FILES['image']
        image_type = request.data.get('type', 'main')
        
        if image_type == 'main':
            # Handle main image
            if product.main_image:
                product.main_image.delete()
            product.main_image = image
        else:
            # Handle additional images
            current_images = product.images or []
            image_path = default_storage.save(
                f'products/additional/{image.name}',
                ContentFile(image.read())
            )
            current_images.append(image_path)
            product.images = current_images
            
        product.save()
        return Response({'message': 'Image uploaded successfully'})

    @action(detail=True, methods=['DELETE'], url_path='remove-image/(?P<image_id>[^/.]+)')
    def remove_image(self, request, pk=None, image_id=None):
        """Handle image removal for products"""
        product = self.get_object()
        
        if image_id == 'main':
            if product.main_image:
                product.main_image.delete()
                product.main_image = None
        else:
            try:
                image_index = int(image_id)
                current_images = product.images
                if 0 <= image_index < len(current_images):
                    # Remove from storage and list
                    default_storage.delete(current_images[image_index])
                    current_images.pop(image_index)
                    product.images = current_images
                else:
                    return Response(
                        {'error': 'Image index out of range'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            except ValueError:
                return Response(
                    {'error': 'Invalid image ID'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        product.save()
        return Response({'message': 'Image removed successfully'})
    @action(detail=False, methods=['GET'])
    def tags(self, request):
        """Get all available tags for product management"""
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_products = Product.objects.filter(is_featured=True)
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def categories(self, request):
        """Get all available categories for product management"""
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'], url_path='upload-images')
    def upload_images(self, request, pk=None):
        """Handle multiple image uploads for products"""
        product = self.get_object()
        
        if 'images' not in request.FILES:
            return Response(
                {'error': 'No images provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_urls = []
        errors = []
        
        # Get current images
        current_images = product.images or []
        
        for image in request.FILES.getlist('images'):
            try:
                # Upload to Cloudinary
                upload_result = upload(
                    image,
                    folder=f'products/{product.id}/',
                    resource_type="image"
                )
                
                # Get the secure URL from the upload result
                image_url = upload_result['secure_url']
                uploaded_urls.append(image_url)
                
                # Add to current images
                current_images.append(image_url)
                
            except Exception as e:
                errors.append(f"Failed to upload {image.name}: {str(e)}")
        
        # Save the updated images list to the product
        product.images = current_images
        product.save()
        
        response_data = {
            'uploaded_images': uploaded_urls,
            'total_uploaded': len(uploaded_urls),
            'all_images': product.images  # Return all images including the new ones
        }
        
        if errors:
            response_data['errors'] = errors
            
        return Response(response_data)
    @action(detail=True, methods=['DELETE'], url_path='remove-images')
    def remove_images(self, request, pk=None):
        """Handle removal of multiple images"""
        product = self.get_object()
        image_urls = request.data.get('image_urls', [])
        
        if not image_urls:
            return Response(
                {'error': 'No image URLs provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        current_images = product.images or []
        removed_urls = []
        
        for url in image_urls:
            if url in current_images:
                current_images.remove(url)
                removed_urls.append(url)
        
        product.images = current_images
        product.save()
        
        return Response({
            'message': 'Images removed successfully',
            'removed_images': removed_urls,
            'remaining_images': product.images
        })

    @action(detail=False, methods=['GET'])
    def sizes(self, request):
        """Get all available sizes for product management"""
        sizes = Size.objects.all()
        serializer = SizeSerializer(sizes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def colors(self, request):
        """Get all available colors for product management"""
        colors = Color.objects.all()
        serializer = ColorSerializer(colors, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def add_sizes(self, request, pk=None):
        """Add available sizes to a product"""
        product = self.get_object()
        size_ids = request.data.get('size_ids', [])
        
        added_sizes = []
        for size_id in size_ids:
            try:
                size = Size.objects.get(id=size_id)
                product_size, created = ProductSize.objects.get_or_create(
                    product=product,
                    size=size
                )
                if created:
                    added_sizes.append(size.name)
            except Size.DoesNotExist:
                pass
        
        return Response({
            'message': f"Added sizes: {', '.join(added_sizes)}",
            'product': product.name
        })

    @action(detail=True, methods=['POST'])
    def add_colors(self, request, pk=None):
        """Add available colors to a product"""
        product = self.get_object()
        color_ids = request.data.get('color_ids', [])
        
        added_colors = []
        for color_id in color_ids:
            try:
                color = Color.objects.get(id=color_id)
                product_color, created = ProductColor.objects.get_or_create(
                    product=product,
                    color=color
                )
                if created:
                    added_colors.append(color.name)
            except Color.DoesNotExist:
                pass
        
        return Response({
            'message': f"Added colors: {', '.join(added_colors)}",
            'product': product.name
        })

    @action(detail=True, methods=['DELETE'])
    def remove_size(self, request, pk=None):
        """Remove an available size from a product"""
        product = self.get_object()
        size_id = request.data.get('size_id')
        
        if not size_id:
            return Response({'error': 'Size ID is required'}, status=400)
        
        deleted, _ = ProductSize.objects.filter(product=product, size_id=size_id).delete()
        
        if deleted:
            return Response({'message': 'Size removed from product'})
        return Response({'message': 'Size not found for this product'}, status=404)

    @action(detail=True, methods=['DELETE'])
    def remove_color(self, request, pk=None):
        """Remove an available color from a product"""
        product = self.get_object()
        color_id = request.data.get('color_id')
        
        if not color_id:
            return Response({'error': 'Color ID is required'}, status=400)
        
        deleted, _ = ProductColor.objects.filter(product=product, color_id=color_id).delete()
        
        if deleted:
            return Response({'message': 'Color removed from product'})
        return Response({'message': 'Color not found for this product'}, status=404)

    @action(detail=False, methods=['GET'])
    def debug_wishlist(self, request):
        """Debug endpoint to check wishlist status"""
        if not request.user.is_authenticated:
            return Response({"error": "Not authenticated"}, status=401)
        
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({"error": "Missing product_id parameter"}, status=400)
        
        try:
            # Find user's wishlist
            wishlist = Wishlist.objects.filter(user=request.user).first()
            
            result = {
                "user": request.user.username,
                "product_id": product_id,
                "has_wishlist": wishlist is not None,
            }
            
            if wishlist:
                # Check if product is in wishlist
                item_exists = WishlistItem.objects.filter(
                    wishlist=wishlist,
                    product_id=product_id
                ).exists()
                
                # Get all wishlist items
                all_items = list(WishlistItem.objects.filter(
                    wishlist=wishlist
                ).values_list('product_id', flat=True))
                
                result.update({
                    "product_in_wishlist": item_exists,
                    "all_wishlist_items": all_items,
                    "wishlist_count": len(all_items)
                })
            
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)})
        
class CarouselViewSet(viewsets.ModelViewSet):
    """ViewSet for managing carousel items"""
    queryset = CarouselItem.objects.all().order_by('order')
    serializer_class = CarouselItemSerializer
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [JWTAuthentication, TokenAuthentication, SessionAuthentication]
    
    def get_permissions(self):
        """
        Override permissions:
        - Admin access required for all operations except public endpoint
        - Public endpoint accessible to anyone
        """
        if self.action == 'public':
            return [AllowAny()]
        return [IsAdminUser()]
    
    def get_serializer_class(self):
        """Use different serializers based on the action"""
        if self.action == 'public':
            return CarouselItemPublicSerializer
        return CarouselItemSerializer
    
    @action(detail=False, methods=['get'])
    def public(self, request):
        """Public endpoint for retrieving active carousel items"""
        limit = int(request.query_params.get('limit', 5))  # Default to 5 items
        items = CarouselItem.objects.filter(active=True).order_by('order')[:limit]
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Endpoint for reordering carousel items"""
        try:
            items_order = request.data.get('items', [])
            
            if not items_order:
                return Response(
                    {"error": "No items provided for reordering"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            with transaction.atomic():
                for item_data in items_order:
                    item_id = item_data.get('id')
                    new_order = item_data.get('order')
                    
                    try:
                        item = CarouselItem.objects.get(id=item_id)
                        item.order = new_order
                        item.save()
                    except CarouselItem.DoesNotExist:
                        continue
            
            return Response({"message": "Items reordered successfully"})
        except Exception as e:
            return Response(
                {"error": f"Failed to reorder items: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
class ProductReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        # Filter reviews by product_id
        product_id = self.kwargs.get('product_id')
        return Review.objects.filter(product_id=product_id)
    
    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        serializer.save(user=self.request.user, product=product)

    @action(detail=False, methods=['get'])
    def summary(self, request, product_id=None):
        """Get review summary statistics for a product"""
        reviews = self.get_queryset()
        summary = {
            'average_rating': reviews.aggregate(Avg('rating'))['rating__avg'] or 0,
            'total_reviews': reviews.count(),
            'rating_breakdown': {
                5: reviews.filter(rating=5).count(),
                4: reviews.filter(rating=4).count(),
                3: reviews.filter(rating=3).count(),
                2: reviews.filter(rating=2).count(),
                1: reviews.filter(rating=1).count(),
            }
        }
        return Response(summary)
    
class CustomerPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CustomerFilterSet(FilterSet):
    created_at = DateFromToRangeFilter()
    orders_count = NumberFilter(method='filter_orders_count')
    balance = NumberFilter(method='filter_balance')

    class Meta:
        model = Customer
        fields = ['created_at', 'orders_count', 'balance']

    def filter_orders_count(self, queryset, name, value):
        return queryset.annotate(
            orders_count=Count('order')
        ).filter(orders_count=value)

    def filter_balance(self, queryset, name, value):
        return queryset.annotate(
            balance=Sum('order__total')
        ).filter(balance=value)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerDetailSerializer
    pagination_class = CustomerPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CustomerFilterSet
    search_fields = ['name', 'email', 'phone']
    ordering_fields = ['created_at', 'name', 'orders_count', 'balance']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            orders_count=Count('order'),
            balance=Sum('order__total')
        )
        
        status = self.request.query_params.get('status')
        if status:
            if status.lower() == 'active':
                queryset = queryset.filter(user__is_active=True)
            elif status.lower() == 'blocked':
                queryset = queryset.filter(user__is_active=False)
        return queryset

    @action(detail=False, methods=['POST'])
    def bulk_action(self, request):
        action = request.data.get('action')
        customer_ids = request.data.get('customer_ids', [])
        select_all = request.data.get('select_all', False)
        exclude_ids = request.data.get('exclude_ids', [])

        if select_all:
            queryset = self.get_queryset()
            if exclude_ids:
                queryset = queryset.exclude(id__in=exclude_ids)
            customer_ids = list(queryset.values_list('id', flat=True))

        if not customer_ids and not select_all:
            return Response({
                'error': 'No customers selected'
            }, status=status.HTTP_400_BAD_REQUEST)

        if action == 'update_status':
            new_status = request.data.get('status')
            if new_status not in ['active', 'blocked']:
                return Response({
                    'error': 'Invalid status'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            Customer.objects.filter(id__in=customer_ids).update(
                user__is_active=(new_status == 'active')
            )

        elif action == 'delete':
            Customer.objects.filter(id__in=customer_ids).delete()

        return Response({'status': 'success', 'affected': len(customer_ids)})

    @action(detail=False, methods=['GET'])
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="customers-{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Status', 'Orders', 'Total Balance'])
        
        for customer in queryset:
            orders_count = Order.objects.filter(customer=customer).count()
            total_balance = Order.objects.filter(customer=customer).aggregate(
                total=Sum('total'))['total'] or 0
            
            writer.writerow([
                customer.id,
                customer.name,
                customer.email,
                customer.phone,
                'Active' if customer.user.is_active else 'Blocked',
                orders_count,
                total_balance
            ])
        
        return response

    @action(detail=True, methods=['GET'])
    def statistics(self, request, pk=None):
        customer = self.get_object()
        orders = Order.objects.filter(customer=customer)
        
        total_orders = orders.count()
        total_spent = orders.aggregate(total=Sum('total'))['total'] or 0
        recent_orders = orders.order_by('-created_at')[:5]
        
        return Response({
            'total_orders': total_orders,
            'total_spent': total_spent,
            'recent_orders': OrderSerializer(recent_orders, many=True).data
        })

    @action(detail=False, methods=['POST'])
    def add_customer(self, request):
        serializer = CustomerCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)