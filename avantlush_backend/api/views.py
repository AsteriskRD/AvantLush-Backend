# Django imports
import json
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .services import CloverPaymentService
from .serializers import CloverWebhookSerializer, CloverPaymentStatusSerializer
from .models import Payment, Order
from django.shortcuts import redirect
from django.http import JsonResponse

logger = logging.getLogger(__name__)
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
from django.db.models import Count, Sum, F, Q, DecimalField, Value
from django.db.models.functions import TruncDate, Coalesce, TruncDay, TruncMonth, TruncWeek
from datetime import timedelta, date

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
from .permissions import IsAdminUser
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
from django.db.models import Count, Sum, Avg, Exists, OuterRef, F
from django.db.models.functions import TruncDate

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
    Color,
    ProductSize,
    ProductColor
    
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
    FlatOrderItemSerializer,
    SummaryChartResponseSerializer, # Added for dashboard chart
    
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

from django.db import transaction

logger = logging.getLogger(__name__)

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
                    # --- FIX: Save first and last name from Google ---
                    user.first_name = first_name or ''
                    user.last_name = last_name or ''
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
                    # --- FIX: Save first and last name from Google ---
                    user.first_name = first_name or ''
                    user.last_name = last_name or ''
                    user.save()
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

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """
    Admin-specific login endpoint that verifies admin privileges
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'success': False,
            'message': 'Email and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(request, email=email, password=password)
    
    if user and (user.is_staff or user.is_superuser):
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'email': user.email,
                'is_admin': True,
                'uuid': str(user.uuid) if hasattr(user, 'uuid') else None
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': 'Invalid credentials or insufficient privileges'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_admin_access(request):
    """
    Endpoint to check if the current user has admin access
    """
    has_access = request.user.is_staff or request.user.is_superuser
    
    return Response({
        'success': True,
        'has_admin_access': has_access
    })

@csrf_exempt
@api_view(['POST'])
@require_http_methods(["POST"])
def clover_hosted_webhook(request):
    """
    Handle Clover Hosted Checkout webhooks
    This endpoint receives notifications when payments are completed, failed, or cancelled
    """
    try:
        # Get raw payload and signature
        payload = request.body.decode('utf-8')
        signature = request.META.get('HTTP_CLOVER_SIGNATURE', '')
        
        logger.info(f"Received Clover webhook - Payload length: {len(payload)}")
        logger.debug(f"Webhook payload: {payload[:500]}...")  # Log first 500 chars for debugging
        
        # Verify webhook signature for security
        clover_service = CloverPaymentService()
        if not clover_service.verify_webhook_signature(payload, signature):
            logger.warning("Invalid Clover webhook signature")
            return HttpResponse('Invalid signature', status=400)
        
        # Parse webhook data
        try:
            webhook_data = json.loads(payload)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in webhook payload: {str(e)}")
            return HttpResponse('Invalid JSON', status=400)
        
        # Validate webhook data structure
        webhook_serializer = CloverWebhookSerializer(data=webhook_data)
        if not webhook_serializer.is_valid():
            logger.error(f"Invalid webhook data structure: {webhook_serializer.errors}")
            return HttpResponse('Invalid webhook data', status=400)
        
        # Extract webhook information
        webhook_type = webhook_data.get('type', '')
        webhook_status = webhook_data.get('status', '')
        checkout_session_id = webhook_data.get('data', '')  # This contains the checkout session UUID
        payment_id = webhook_data.get('id', '')
        
        logger.info(f"Processing webhook - Type: {webhook_type}, Status: {webhook_status}, Session: {checkout_session_id}")
        
        # Find the payment record by checkout session ID
        try:
            payment = Payment.objects.get(clover_checkout_session_id=checkout_session_id)
            order = payment.order
            
            logger.info(f"Found payment record for order {order.order_number}")
            
            # Update payment and order status based on webhook status
            if webhook_status == 'APPROVED':
                payment.status = 'COMPLETED'
                payment.clover_payment_id = payment_id
                payment.transaction_id = payment_id or payment.transaction_id
                
                # Update order status
                order.status = 'PROCESSING'
                order.payment_status = 'PAID'
                order.save()
                
                logger.info(f"Payment approved for order {order.order_number}")
                
            elif webhook_status == 'DECLINED':
                payment.status = 'FAILED'
                order.status = 'CANCELLED'
                order.payment_status = 'FAILED'
                order.save()
                
                logger.info(f"Payment declined for order {order.order_number}")
                
            elif webhook_status == 'CANCELLED':
                payment.status = 'CANCELLED'
                # Don't change order status - user might try again with different payment method
                
                logger.info(f"Payment cancelled for order {order.order_number}")
            
            else:
                logger.warning(f"Unknown webhook status: {webhook_status}")
            
            # Store complete webhook response for debugging and audit trail
            payment.gateway_response = webhook_data
            payment.save()
            
            logger.info(f"Payment record updated successfully for session {checkout_session_id}")
            
        except Payment.DoesNotExist:
            logger.warning(f"Payment not found for checkout session: {checkout_session_id}")
            # This might be a webhook for a session we don't know about
            # Return 200 to prevent Clover from retrying
            return HttpResponse('Payment not found', status=200)
        
        except Exception as e:
            logger.error(f"Error processing payment update: {str(e)}")
            return HttpResponse(f'Payment processing error: {str(e)}', status=500)
        
        return HttpResponse('OK', status=200)
        
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return HttpResponse(f'Webhook error: {str(e)}', status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # 🔧 CHANGE: Require authentication for production
def create_clover_hosted_checkout(request):
    """
    Create order in database FIRST, then create Clover checkout session
    """
    try:
        data = request.data
        print(f"🔍 DEBUG: Creating order + Clover checkout for: {data}")
        print(f"🔍 DEBUG: Authenticated user: {request.user.email if request.user.is_authenticated else 'Anonymous'}")
        
        # 🔧 FIX: Proper authentication handling
        if not request.user.is_authenticated:
            return Response({
                'is_success': False,
                'data': {
                    'status': 'error',
                    'message': 'Authentication required. Please login first.',
                    'code': 'AUTH_REQUIRED'
                }
            }, status=401)
        
        # STEP 1: Validate required fields
        if not data.get('total_amount'):
            return Response({
                'is_success': False,
                'data': {
                    'status': 'error',
                    'message': 'total_amount is required'
                }
            }, status=400)
        
        # STEP 2: Create Order in Database FIRST
        with transaction.atomic():
            # 🔧 FIX: Use the authenticated user's cart
            cart = Cart.objects.filter(user=request.user).first()
            if not cart:
                cart = Cart.objects.create(user=request.user)
                print(f"✅ Created new cart for user: {request.user.email}")
            else:
                print(f"✅ Using existing cart for user: {request.user.email}")
            
            cart_items = CartItem.objects.filter(cart=cart).select_related('product')
            
            # For testing, create a cart item if none exist
            if not cart_items.exists():
                from avantlush_backend.api.models import Product
                product = Product.objects.first()
                if product:
                    cart_item = CartItem.objects.create(
                        cart=cart,
                        product=product,
                        quantity=1
                    )
                    cart_items = CartItem.objects.filter(cart=cart).select_related('product')
                    print(f"✅ Created test cart item for user: {request.user.email}")
                else:
                    return Response({
                        'is_success': False,
                        'data': {
                            'status': 'error',
                            'message': 'No products found. Create a product first.'
                        }
                    }, status=400)
            
            # Create the order for the authenticated user
            shipping_address = data.get('shipping_address', {})
            order = Order.objects.create(
                user=request.user,  # 🔧 FIX: Always use authenticated user
                shipping_address=shipping_address.get('street_address', '123 Test St'),
                shipping_city=shipping_address.get('city', 'Test City'),
                shipping_state=shipping_address.get('state', 'CA'),
                shipping_country=shipping_address.get('country', 'US'),
                shipping_zip=shipping_address.get('zip_code', '12345'),
                shipping_cost=Decimal(data.get('shipping_cost', '4.99')),
                subtotal=Decimal('0.00'),
                total=Decimal(data['total_amount']),
                status='PENDING',
                payment_status='PENDING'
            )
            
            # Create order items from cart
            subtotal = Decimal('0.00')
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                subtotal += cart_item.product.price * cart_item.quantity
                
                # Update stock
                cart_item.product.stock_quantity -= cart_item.quantity
                cart_item.product.save()
            
            # Update order totals
            order.subtotal = subtotal
            order.save()
            
            print(f"✅ Created Order #{order.id} - {order.order_number} for user: {request.user.email}")
        
        # STEP 3: Create Clover Hosted Checkout Session with proper user data
        clover_order_data = {
            'total_amount': float(order.total),
            'currency': 'USD',
            'order_number': order.order_number,
            'order_id': order.id,
            'customer': {
                'email': request.user.email,  # 🔧 FIX: Use actual authenticated user
                'firstName': request.user.first_name or 'Customer',
                'lastName': request.user.last_name or '',
                'phoneNumber': getattr(request.user, 'phone_number', '555-555-0000')
            },
            # 🔧 FIX: Use proper redirect URLs
            'redirect_urls': {
                'success': f"https://httpbin.org/get?status=success&order_id={order.id}&user={request.user.email}",
                'failure': f"https://httpbin.org/get?status=failure&order_id={order.id}&user={request.user.email}",
                'cancel': f"https://httpbin.org/get?status=cancel&order_id={order.id}&user={request.user.email}"
            }
        }
        
        print(f"🔧 DEBUG: Using URLs for user {request.user.email}: {clover_order_data['redirect_urls']}")
        
        clover_service = CloverPaymentService()
        result = clover_service.create_hosted_checkout_session(clover_order_data)
        
        if result['success']:
            # Store Clover session info in order
            order.clover_session_id = result.get('session_id')
            order.save()
            
            # Clear cart after successful order creation
            cart_items.delete()
            print(f"✅ Cleared cart for user: {request.user.email}")
            
            return Response({
                'is_success': True,
                'data': {
                    'status': 'success',
                    'message': f'Order created for {request.user.email}',
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'checkout_url': result['checkout_url'],
                    'session_id': result['session_id'],
                    'total_amount': float(order.total),
                    'user_email': request.user.email,  # 🔧 ADD: Include user info
                    'instructions': 'Visit checkout_url to complete payment'
                }
            })
        else:
            # If Clover fails, mark order as failed
            order.status = 'FAILED'
            order.save()
            
            return Response({
                'is_success': False,
                'data': {
                    'status': 'error',
                    'message': f'Checkout session creation failed: {result["error"]}',
                    'order_id': order.id,
                    'user_email': request.user.email
                }
            }, status=400)
    
    except Exception as e:
        print(f"❌ ERROR in create_clover_hosted_checkout: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'is_success': False,
            'data': {
                'status': 'error',
                'message': f'Order creation failed: {str(e)}',
                'user_email': request.user.email if request.user.is_authenticated else 'Anonymous'
            }
        }, status=500)


# 🔧 ADD: Order refresh endpoint for frontend
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def refresh_user_orders(request):
    """Force refresh user's orders - useful for frontend"""
    try:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        
        # Clear any cache if you're using one
        from django.core.cache import cache
        cache_key = f"user_orders_{request.user.id}"
        cache.delete(cache_key)
        
        # Use your existing OrderSerializer
        from .serializers import OrderSerializer
        serializer = OrderSerializer(orders, many=True)
        
        return Response({
            'success': True,
            'count': orders.count(),
            'orders': serializer.data,
            'user': request.user.email,
            'refreshed_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'user': request.user.email
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_clover_hosted_checkout_test(request):
    """
    TEST ONLY: Create order without authentication for development
    """
    try:
        data = request.data
        print(f"🧪 TEST: Creating order + Clover checkout for: {data}")
        
        # Get or create a test user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # 🔧 FIX: Remove email_verified field and use correct fields
        test_user, created = User.objects.get_or_create(
            email='test-checkout@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True,
                # Remove email_verified - it doesn't exist in your model
            }
        )
        
        if created:
            test_user.set_password('TestPassword123!')
            test_user.save()
            print(f"🧪 Created new test user: {test_user.email}")
        
        print(f"🧪 TEST: Using test user: {test_user.email}")
        
        # STEP 1: Validate required fields
        if not data.get('total_amount'):
            return Response({
                'is_success': False,
                'data': {
                    'status': 'error',
                    'message': 'total_amount is required'
                }
            }, status=400)
        
        # STEP 2: Create Order in Database FIRST
        with transaction.atomic():
            # Use the test user's cart
            cart, cart_created = Cart.objects.get_or_create(user=test_user)
            if cart_created:
                print(f"✅ Created new cart for test user: {test_user.email}")
            else:
                print(f"✅ Using existing cart for test user: {test_user.email}")
            
            cart_items = CartItem.objects.filter(cart=cart).select_related('product')
            
            # For testing, create a cart item if none exist
            if not cart_items.exists():
                from avantlush_backend.api.models import Product
                product = Product.objects.first()
                if product:
                    cart_item = CartItem.objects.create(
                        cart=cart,
                        product=product,
                        quantity=1
                    )
                    cart_items = CartItem.objects.filter(cart=cart).select_related('product')
                    print(f"✅ Created test cart item for user: {test_user.email}")
                else:
                    return Response({
                        'is_success': False,
                        'data': {
                            'status': 'error',
                            'message': 'No products found. Create a product first.'
                        }
                    }, status=400)
            
            # Create the order for the test user
            shipping_address = data.get('shipping_address', {})
            order = Order.objects.create(
                user=test_user,
                shipping_address=shipping_address.get('street_address', '123 Test St'),
                shipping_city=shipping_address.get('city', 'Test City'),
                shipping_state=shipping_address.get('state', 'CA'),
                shipping_country=shipping_address.get('country', 'US'),
                shipping_zip=shipping_address.get('zip_code', '12345'),
                shipping_cost=Decimal(str(data.get('shipping_cost', '4.99'))),
                subtotal=Decimal('0.00'),
                total=Decimal(str(data['total_amount'])),
                status='PENDING',
                payment_status='PENDING'
            )
            
            # Create order items from cart
            subtotal = Decimal('0.00')
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                subtotal += cart_item.product.price * cart_item.quantity
                
                # Update stock (with safety check)
                if cart_item.product.stock_quantity >= cart_item.quantity:
                    cart_item.product.stock_quantity -= cart_item.quantity
                    cart_item.product.save()
            
            # Update order totals
            order.subtotal = subtotal
            order.save()
            
            print(f"✅ Created Test Order #{order.id} - {order.order_number} for user: {test_user.email}")
        
        # STEP 3: Create Clover Hosted Checkout Session
        clover_order_data = {
            'total_amount': float(order.total),
            'currency': 'USD',
            'order_number': order.order_number,
            'order_id': order.id,
            'customer': {
                'email': test_user.email,
                'firstName': test_user.first_name or 'Test',
                'lastName': test_user.last_name or 'User',
                'phoneNumber': '555-555-0000'
            },
            'redirect_urls': {
                'success': f"https://httpbin.org/get?status=success&order_id={order.id}&user={test_user.email}",
                'failure': f"https://httpbin.org/get?status=failure&order_id={order.id}&user={test_user.email}",
                'cancel': f"https://httpbin.org/get?status=cancel&order_id={order.id}&user={test_user.email}"
            }
        }
        
        print(f"🔧 DEBUG: Using URLs for test user {test_user.email}: {clover_order_data['redirect_urls']}")
        
        clover_service = CloverPaymentService()
        result = clover_service.create_hosted_checkout_session(clover_order_data)
        
        if result['success']:
            # Store Clover session info in order
            order.clover_session_id = result.get('session_id')
            order.save()
            
            # Clear cart after successful order creation
            cart_items.delete()
            print(f"✅ Cleared cart for test user: {test_user.email}")
            
            return Response({
                'is_success': True,
                'data': {
                    'status': 'success',
                    'message': f'Test order created for {test_user.email}',
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'checkout_url': result['checkout_url'],
                    'session_id': result['session_id'],
                    'total_amount': float(order.total),
                    'user_email': test_user.email,
                    'instructions': 'Visit checkout_url to complete payment'
                }
            })
        else:
            # If Clover fails, mark order as failed
            order.status = 'FAILED'
            order.save()
            
            return Response({
                'is_success': False,
                'data': {
                    'status': 'error',
                    'message': f'Test checkout session creation failed: {result["error"]}',
                    'order_id': order.id,
                    'user_email': test_user.email
                }
            }, status=400)
    
    except Exception as e:
        print(f"❌ TEST ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'is_success': False,
            'data': {
                'status': 'error',
                'message': f'Test order creation failed: {str(e)}'
            }
        }, status=500)




@api_view(['GET'])
def clover_hosted_payment_status(request, order_id):
    """
    Check payment status for an existing order
    """
    try:
        # Get the order (now it exists!)
        order = Order.objects.get(id=order_id)
        
        # Check if payment already processed
        existing_payment = Payment.objects.filter(order=order).first()
        if existing_payment:
            return Response({
                'order_id': order.id,
                'payment_status': existing_payment.status,
                'order_status': order.status,
                'amount': float(order.total),
                'session_id': getattr(order, 'clover_session_id', None),
                'payment_id': existing_payment.transaction_id,
                'created_at': order.created_at,
                'updated_at': order.updated_at
            })
        
        # If no payment found, order is still pending
        return Response({
            'order_id': order.id,
            'payment_status': 'PENDING',
            'order_status': order.status,
            'amount': float(order.total),
            'session_id': getattr(order, 'clover_session_id', None),
            'created_at': order.created_at,
            'updated_at': order.updated_at
        })
        
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found'
        }, status=404)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)

# Add this helper view to get all payments for an order (useful for debugging)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_payments_list(request, order_id):
    """
    Get all payment attempts for an order
    Useful for debugging and customer service
    """
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        payments = Payment.objects.filter(order=order).order_by('-created_at')
        
        payments_data = []
        for payment in payments:
            payments_data.append({
                'id': payment.id,
                'payment_method': payment.payment_method,
                'status': payment.status,
                'amount': payment.amount,
                'transaction_id': payment.transaction_id,
                'created_at': payment.created_at,
                'clover_session_id': payment.clover_checkout_session_id,
                'clover_payment_id': payment.clover_payment_id
            })
        
        return Response({
            'order_id': order.id,
            'order_number': order.order_number,
            'payments': payments_data
        })
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)

@api_view(['POST'])
def test_complete_checkout(request):
    """Test complete checkout flow - no auth required"""
    try:
        from django.contrib.auth import get_user_model
        
        data = request.data
        print(f"🔍 DEBUG: Received test checkout data: {data}")
        
        # Get or create a test user for the order
        User = get_user_model()
        test_user, created = User.objects.get_or_create(
            email='test-checkout@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'Checkout',
                'is_active': True
            }
        )
        
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            print(f"✅ Created test user: {test_user.email}")
        else:
            print(f"✅ Using existing test user: {test_user.email}")
        
        # Create test order WITH user
        order = Order.objects.create(
            user=test_user,  # ✅ Add the required user field
            order_number=f"TEST-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            total=Decimal(str(data.get('total_amount', 75.00))),
            subtotal=Decimal(str(data.get('total_amount', 75.00))) - Decimal('5.00'),
            shipping_cost=Decimal('5.00'),
            status='PENDING',
            payment_status='PENDING',
            shipping_address="123 Test St, Test City, CA 12345",
            shipping_city="Test City",
            shipping_state="CA",
            shipping_country="US",
            shipping_zip="12345"
        )
        
        print(f"✅ Created test order: {order.order_number} for user: {test_user.email}")
        
        # Process payment using your method
        payment_data = {'card_data': data.get('card_data', {})}
        
        # Create a mock CheckoutViewSet instance to use the method
        checkout_view = CheckoutViewSet()
        result = checkout_view._process_clover_direct_payment(order, payment_data, False)
        
        return result
        
    except Exception as e:
        logger.error(f"Test checkout error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


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

from django.http import JsonResponse

@csrf_exempt
def checkout_success(request):
    """Handle successful payment redirects from Clover"""
    try:
        order_id = request.GET.get('order_id')
        session_id = request.GET.get('session_id')
        
        if not order_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing order_id parameter'
            }, status=400)
        
        # Get the order
        order = Order.objects.get(id=order_id)
        
        # Create payment record if not exists
        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                'amount': order.total,
                'payment_method': 'CLOVER_HOSTED',
                'transaction_id': session_id or f"clover-{order.id}",
                'status': 'COMPLETED',
                'gateway_response': dict(request.GET)
            }
        )
        
        # Update order status
        order.status = 'PROCESSING'
        order.payment_status = 'PAID'
        order.save()
        
        print(f"✅ Payment completed for Order #{order.id}")
        
        # Redirect to frontend success page
        frontend_success_url = f"{settings.FRONTEND_URL}/checkout/success?order_id={order.id}&order_number={order.order_number}"
        
        return JsonResponse({
            'status': 'success',
            'message': 'Payment completed successfully!',
            'order_id': order.id,
            'order_number': order.order_number,
            'redirect_url': frontend_success_url,
            'payment_id': payment.id
        })
        
    except Order.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Order not found'
        }, status=404)
    except Exception as e:
        print(f"❌ Error in checkout_success: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt 
def checkout_failure(request):
    """Handle failed payment redirects from Clover"""
    try:
        error_code = request.GET.get('error_code')
        error_message = request.GET.get('error_message', 'Payment failed')
        session_id = request.GET.get('session_id') or request.GET.get('checkoutSessionId')
        
        logger.error(f"Clover checkout failure: error_code={error_code}, error_message={error_message}")
        logger.info(f"All GET parameters: {dict(request.GET)}")
        
        # Build frontend failure URL
        frontend_url = f"{settings.FRONTEND_URL}/checkout/failure"
        params = []
        
        if error_code:
            params.append(f"error_code={error_code}")
        if error_message:
            params.append(f"error_message={error_message}")
        if session_id:
            params.append(f"session_id={session_id}")
            
        if params:
            frontend_url += "?" + "&".join(params)
            
        return redirect(frontend_url)
        
    except Exception as e:
        logger.error(f"Error in checkout_failure: {str(e)}")
        return redirect(f"{settings.FRONTEND_URL}/checkout/error?message=redirect_error")

@csrf_exempt
def checkout_cancel(request):
    """Handle cancelled payment redirects from Clover"""
    try:
        session_id = request.GET.get('session_id') or request.GET.get('checkoutSessionId')
        
        logger.info(f"Clover checkout cancelled: session_id={session_id}")
        logger.info(f"All GET parameters: {dict(request.GET)}")
        
        # Build frontend cancel URL
        frontend_url = f"{settings.FRONTEND_URL}/checkout/cancel"
        if session_id:
            frontend_url += f"?session_id={session_id}"
            
        return redirect(frontend_url)
        
    except Exception as e:
        logger.error(f"Error in checkout_cancel: {str(e)}")
        return redirect(f"{settings.FRONTEND_URL}/checkout/error?message=redirect_error")

@api_view(['GET'])
@permission_classes([AllowAny])
def checkout_status_api(request):
    """API endpoint to check checkout status"""
    session_id = request.GET.get('session_id')
    order_id = request.GET.get('order_id')
    
    if not session_id:
        return Response({
            'success': False,
            'message': 'session_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Here you would check the payment status with Clover
        # For now, return basic info
        return Response({
            'success': True,
            'session_id': session_id,
            'order_id': order_id,
            'status': 'completed'  # This should come from actual Clover API call
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart = self.get_cart()  # Remove the request parameter
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        size_id = request.data.get('size_id')
        color_id = request.data.get('color_id')
        
        try:
            product = Product.objects.get(id=product_id)
            
            # Get size and color objects if IDs are provided
            size = Size.objects.get(id=size_id) if size_id else None
            color = Color.objects.get(id=color_id) if color_id else None
            
            # Check if this product variant is already in the cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                size=size,
                color=color,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # If the item already exists, update the quantity
                cart_item.quantity += quantity
                cart_item.save()
            
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Size.DoesNotExist:
            return Response(
                {'error': 'Size not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Color.DoesNotExist:
            return Response(
                {'error': 'Color not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
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
    
    @action(detail=False, methods=['POST'])
    def create_clover_hosted_checkout(self, request):
        """
        Create Clover Hosted Checkout session
        POST /api/checkout/clover-hosted/create/
        """
        try:
            # Validate request data
            from .serializers import CloverHostedCheckoutRequestSerializer
            serializer = CloverHostedCheckoutRequestSerializer(
                data=request.data, 
                context={'request': request}
            )
            
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Invalid request data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            order_id = serializer.validated_data['order_id']
            order = Order.objects.get(id=order_id, user=request.user)
            
            # Check if order already has a pending payment
            existing_payment = Payment.objects.filter(
                order=order,
                payment_method='CLOVER_HOSTED',
                status='PENDING'
            ).first()
            
            if existing_payment and existing_payment.clover_checkout_url:
                # Return existing checkout URL if still valid
                return Response({
                    'success': True,
                    'checkout_url': existing_payment.clover_checkout_url,
                    'session_id': existing_payment.clover_checkout_session_id,
                    'message': 'Using existing checkout session'
                })
            
            # Prepare customer data
            customer_data = {'email': request.user.email}
            
            # Get customer info from profile if available
            if hasattr(request.user, 'profile') and request.user.profile:
                profile = request.user.profile
                if profile.full_name:
                    name_parts = profile.full_name.split(' ', 1)
                    customer_data['first_name'] = name_parts[0]
                    if len(name_parts) > 1:
                        customer_data['last_name'] = name_parts[1]
                if profile.phone_number:
                    customer_data['phone'] = profile.phone_number
            
            # Prepare order items
            items_data = []
            for item in order.items.all():
                items_data.append({
                    'name': item.product.name,
                    'price': str(item.price),
                    'quantity': item.quantity,
                    'description': item.product.description[:100] if item.product.description else ''
                })
            
            # Prepare redirect URLs
            success_url = serializer.validated_data.get('success_url')
            failure_url = serializer.validated_data.get('failure_url')
            
            redirect_urls = {
                'success': success_url or f"{settings.FRONTEND_URL}/checkout/success?order_id={order.id}",
                'failure': failure_url or f"{settings.FRONTEND_URL}/checkout/failure?order_id={order.id}"
            }
            
            # Prepare order data for Clover
            order_data = {
                'customer': customer_data,
                'items': items_data,
                'redirect_urls': redirect_urls,
                'order_id': order.id,
                'order_number': order.order_number,
                'total_amount': float(order.total)
            }
            
            # Create Clover hosted checkout session
            clover_service = CloverPaymentService()
            result = clover_service.create_hosted_checkout_session(order_data)
            
            if result['success']:
                # Create or update payment record
                payment, created = Payment.objects.get_or_create(
                    order=order,
                    payment_method='CLOVER_HOSTED',
                    defaults={
                        'amount': order.total,
                        'status': 'PENDING',
                        'transaction_id': f"clover_hosted_{order.id}_{timezone.now().timestamp()}"
                    }
                )
                
                # Store Clover session details
                payment.clover_checkout_session_id = result['session_id']
                payment.clover_checkout_url = result['checkout_url']
                payment.save()
                
                logger.info(f"Clover hosted checkout created for order {order.order_number}")
                
                return Response({
                    'success': True,
                    'checkout_url': result['checkout_url'],
                    'session_id': result['session_id'],
                    'expires_at': result.get('expires_at'),
                    'message': 'Clover checkout session created successfully'
                })
            else:
                logger.error(f"Failed to create Clover checkout: {result.get('error')}")
                return Response({
                    'success': False,
                    'error': result.get('error', 'Failed to create checkout session')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Order not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Clover checkout creation failed: {str(e)}")
            return Response({
                'success': False,
                'error': f'Failed to create checkout session: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
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
            
            # Fix: Get customer name properly
            customer_name = ""
            if hasattr(order, 'customer') and order.customer:
                customer_name = order.customer.name
            elif order.user:
                # Try to get name from user or profile
                if hasattr(order.user, 'profile') and order.user.profile:
                    customer_name = order.user.profile.full_name or order.user.email
                else:
                    customer_name = order.user.email
                    
            writer.writerow([
                order.order_number,
                order.created_at.strftime('%Y-%m-%d %H:%M'),
                customer_name,  # Use the fixed customer name
                order.user.email if order.user else 'Guest',
                items_str,
                order.total,
                order.get_status_display() if hasattr(order, 'get_status_display') else order.status,
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
    
    @action(detail=False, methods=['GET'])
    def flat_orders(self, request):
        """Get orders with each item as a separate entry"""
        queryset = OrderItem.objects.all().select_related(
            'order', 'order__user', 'product'
        ).prefetch_related('order__tracking_history').order_by('-order__created_at', 'id')
        
        # Apply filters if needed
        if not request.user.is_staff:
            queryset = queryset.filter(order__user=request.user)
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FlatOrderItemSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = FlatOrderItemSerializer(queryset, many=True)
        return Response(serializer.data)

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
    
class OrderCreateView(generics.CreateAPIView):
    """Create new order - matches your 'Create Order' button"""
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAdminUser]
    
    def perform_create(self, serializer):
        # If no user is provided, create order for selected customer
        customer_id = self.request.data.get('customer_id')
        if customer_id:
            customer = Customer.objects.get(id=customer_id)
            if customer.user:
                serializer.save(user=customer.user, customer=customer)
            else:
                # Handle case where customer has no user account
                serializer.save(customer=customer)
        else:
            serializer.save(user=self.request.user)

class OrderUpdateView(generics.RetrieveUpdateAPIView):
    """Update existing order - for editing orders"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]

@api_view(['GET'])
def product_search(request):
    """Product search API - matches your product search box"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return Response([])
    
    products = Product.objects.filter(
        Q(name__icontains=query) | 
        Q(sku__icontains=query) |
        Q(description__icontains=query),
        status='active'
    )[:10]  # Limit to 10 results
    
    # Simple product data for search dropdown
    product_data = [{
        'id': p.id,
        'name': p.name,
        'sku': p.sku,
        'price': str(p.price),
        'stock_quantity': p.stock_quantity,
        'image': p.main_image.url if p.main_image else None
    } for p in products]
    
    return Response(product_data)

@api_view(['GET'])
def order_choices(request):
    """Get all dropdown choices for order form"""
    return Response({
        'payment_types': Order.PAYMENT_TYPE_CHOICES,
        'order_types': Order.ORDER_TYPE_CHOICES,
        'status_choices': Order.STATUS_CHOICES,
    })

class ProductDetailForOrderView(generics.RetrieveAPIView):
    """Get product details when adding to order"""
    queryset = Product.objects.filter(status='active')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]

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
                    'name': 'Clover Direct',
                    'enabled': True,
                    'type': 'card'
                },
                {
                    'id': 'clover_hosted', 
                    'name': 'Clover Secure Checkout', 
                    'enabled': True, 
                    'type': 'redirect'
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
            
            # Handle Clover Direct Payment
            if payment_method.upper() == 'CLOVER' or payment_method == 'clover_direct':
                return self._process_clover_direct_payment(order, payment_data, save_card)
            
            # Handle other payment methods
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
                
                order.status = 'PROCESSING'  # Changed from 'PAID' to 'PROCESSING'
                order.payment_status = 'PAID'  # Add this line
                order.save()
                
                return Response({
                    'status': 'success',
                    'payment_id': payment.id,
                    'transaction_id': result['transaction_id']
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
            'CLOVER_HOSTED': CloverPaymentService(),
        }
        return services.get(payment_method.upper())

    def _process_clover_direct_payment(self, order, payment_data, save_card):
        """Process Clover direct payment"""
        try:
            # Extract card data
            card_data = payment_data.get('card_data', {})
            if not card_data:
                return Response({
                    'status': 'error',
                    'message': 'Card data is required for Clover direct payment'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Prepare order data for Clover
            order_data = {
                'total_amount': float(order.total),
                'order_number': order.order_number,
                'order_id': str(order.id),
                'currency': 'USD'
            }
            
            # Initialize Clover service and process payment
            clover_service = CloverPaymentService()
            result = clover_service.process_direct_payment(order_data, card_data)
            
            if result['success']:
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    amount=order.total,
                    payment_method='CLOVER',
                    transaction_id=result['transaction_id'],
                    status='COMPLETED',
                    gateway_response=result.get('response', {}),
                    card_last_four=result.get('card_last_four', ''),
                    card_brand=result.get('card_brand', ''),
                    save_card=save_card
                )
                
                # Update order status
                order.status = 'PROCESSING'
                order.payment_status = 'PAID'
                order.save()

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
