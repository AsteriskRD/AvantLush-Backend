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


from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from cloudinary.uploader import upload as cloudinary_upload
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
    ProductColor,
    ProductVariation,
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
    CategoryCreateSerializer,
    ReviewSummarySerializer,
    OrderCreateSerializer,
    OrderItemSerializer,
    CustomerSerializer,
    CustomerDetailSerializer,
    CustomerCreateSerializer,
    CustomerUpdateSerializer,
    CarouselItemSerializer,
    UserDetailsUpdateSerializer,
    CarouselItemPublicSerializer,
    SizeSerializer,
    ColorSerializer,
    FlatOrderItemSerializer,
    SummaryChartResponseSerializer, # Added for dashboard chart
    OrderNotificationSerializer,
    ProductVariationManagementSerializer,
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
                # Check stock before creating order item and subtracting
                if cart_item.product.stock_quantity < cart_item.quantity:
                    return Response({
                        'is_success': False,
                        'data': {
                            'status': 'error',
                            'message': f'Not enough stock for {cart_item.product.name}. Available: {cart_item.product.stock_quantity}, Requested: {cart_item.quantity}'
                        }
                    }, status=400)
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
            # 🔧 FIX: Use HTTPS URLs for Clover redirect URLs during development
            'redirect_urls': {
                'success': f"https://avantlush.com/checkout/success?order_id={order.id}&user={request.user.email}",
                'failure': f"https://avantlush.com/checkout/failure?order_id={order.id}&user={request.user.email}",
                'cancel': f"https://avantlush.com/checkout/cancel?order_id={order.id}&user={request.user.email}"
            }
        }
        
        print(f"🔧 DEBUG: Using URLs for user {request.user.email}: {clover_order_data['redirect_urls']}")
        
        clover_service = CloverPaymentService()
        result = clover_service.create_hosted_checkout_session(clover_order_data)
        
        if result['success']:
            # Store Clover session info in order
            order.clover_session_id = result.get('session_id')
            order.save()
            
            # Removed: cart_items.delete() here. Cart will be cleared after payment confirmation.
            # print(f"✅ Cleared cart for user: {request.user.email}")
            
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
        import json
        data = request.data
        print(f"🧪 TEST: Creating order + Clover checkout for: {data} (type: {type(data)})")
        # Defensive: If data is a string, try to parse as JSON
        if isinstance(data, str):
            try:
                data = json.loads(data)
                print(f"🧪 TEST: Parsed string data to dict: {data}")
            except Exception as parse_exc:
                print(f"❌ TEST ERROR: Could not parse string data as JSON: {parse_exc}")
                return Response({
                    'is_success': False,
                    'data': {
                        'status': 'error',
                        'message': f'Invalid JSON payload: {parse_exc}'
                    }
                }, status=400)
        
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
                'success': f"https://avantlush.com/checkout/success?order_id={order.id}&user={test_user.email}",
                'failure': f"https://avantlush.com/checkout/failure?order_id={order.id}&user={test_user.email}",
                'cancel': f"https://avantlush.com/checkout/cancel?order_id={order.id}&user={test_user.email}"
            }
        }
        
        print(f"🔧 DEBUG: Using URLs for test user {test_user.email}: {clover_order_data['redirect_urls']}")
        
        clover_service = CloverPaymentService()
        result = clover_service.create_hosted_checkout_session(clover_order_data)
        
        if result['success']:
            # Store Clover session info in order
            order.clover_session_id = result.get('session_id')
            order.save()
            
            # Removed: cart_items.delete() here. Cart will be cleared after payment confirmation.
            # print(f"✅ Cleared cart for test user: {test_user.email}")
            
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
        
        # Support both old format (size_id, color_id) and new format (size, color)
        size_id = request.data.get('size_id')
        color_id = request.data.get('color_id')
        size_name = request.data.get('size') or request.data.get('size_name')
        color_name = request.data.get('color') or request.data.get('color_name')
        
        try:
            product = Product.objects.get(id=product_id)
            
            # Resolve size: prefer ID, then name
            size = None
            if size_id:
                try:
                    size = Size.objects.get(id=size_id)
                except Size.DoesNotExist:
                    pass
            elif size_name:
                size, _ = Size.objects.get_or_create(name=size_name)
            
            # Resolve color: prefer ID, then name
            color = None
            if color_id:
                try:
                    color = Color.objects.get(id=color_id)
                except Color.DoesNotExist:
                    pass
            elif color_name:
                color, _ = Color.objects.get_or_create(name=color_name)
            
            # Find the specific variation for stock checking
            variation = None
            if size and color:
                from .models import ProductVariation
                variation = ProductVariation.objects.filter(
                    product=product,
                    sizes=size,
                    colors=color
                ).first()
            
            # Check stock availability if variation exists
            if variation:
                available = variation.available_quantity
                if quantity > available:
                    return Response({
                        'error': f'Only {available} units available for {size.name} {color.name}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if this product variant is already in the cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                size=size,
                color=color,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # If the item already exists, check total quantity
                new_total_quantity = cart_item.quantity + quantity
                if variation and new_total_quantity > variation.available_quantity:
                    return Response({
                        'error': f'Only {variation.available_quantity} units available. You already have {cart_item.quantity} in cart.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Update the quantity
                cart_item.quantity += quantity
                cart_item.save()
            
            # Reserve stock if variation exists
            if variation:
                variation.reserved_quantity += quantity
                variation.save()
                
                # Check if product should be auto-drafted
                if variation.available_quantity == 0:
                    product.status = 'draft'
                    product.save()
            
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
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
            
            # Release reserved stock if variation exists
            if cart_item.size and cart_item.color:
                from .models import ProductVariation
                variation = ProductVariation.objects.filter(
                    product=cart_item.product,
                    sizes=cart_item.size,
                    colors=cart_item.color
                ).first()
                
                if variation:
                    # Release reserved stock
                    variation.reserved_quantity -= cart_item.quantity
                    variation.save()
                    
                    # Check if product should be reactivated
                    if variation.available_quantity > 0 and cart_item.product.status == 'draft':
                        cart_item.product.status = 'active'
                        cart_item.product.save()
            
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
        
        # Release all reserved stock before clearing cart
        for cart_item in cart.items.all():
            if cart_item.size and cart_item.color:
                from .models import ProductVariation
                variation = ProductVariation.objects.filter(
                    product=cart_item.product,
                    sizes=cart_item.size,
                    colors=cart_item.color
                ).first()
                
                if variation:
                    # Release reserved stock
                    variation.reserved_quantity -= cart_item.quantity
                    variation.save()
                    
                    # Check if product should be reactivated
                    if variation.available_quantity > 0 and cart_item.product.status == 'draft':
                        cart_item.product.status = 'active'
                        cart_item.product.save()
        
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
    search_fields = ['order_number', 'user__email', 'user__first_name', 'user__last_name', 'items__product__name']
    ordering_fields = ['created_at', 'total', 'status']
    ordering = ['-created_at']
    permission_classes = [IsAdminUser]  # Default: Only admin users can access orders

    def get_permissions(self):
        """
        Override permissions:
        - Admin access required for management operations
        - Authenticated users can access their own orders for read-only operations
        """
        if self.action in ['list', 'retrieve', 'flat_orders', 'tracking_history']:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Admin users can see all orders, regular users only see their own
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def list(self, request, *args, **kwargs):
        """Override list to ensure proper filtering and search"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
                
                # Clear user's cart ONLY after payment is confirmed
                try:
                    cart = Cart.objects.get(user=order.user)
                    cart.items.all().delete()
                except Cart.DoesNotExist:
                    pass
                
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
                
                # Clear user's cart
                try:
                    cart = Cart.objects.get(user=order.user)
                    cart.items.all().delete()
                except Cart.DoesNotExist:
                    pass
                
                return Response({
                    'status': 'success',
                    'message': 'Payment processed successfully',
                    'payment_id': payment.id,
                    'transaction_id': result['transaction_id'],
                    'order_id': order.id,
                    'order_number': order.order_number
                })
            else:
                return Response({
                    'status': 'error',
                    'message': result.get('error', 'Payment failed'),
                    'details': result.get('details', {})
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Clover direct payment error: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Payment processing error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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

@api_view(['GET'])
def payment_methods(request):
    """Get available payment methods - Simple endpoint"""
    return Response({
        "success": True,
        "payment_methods": [
            {
                "id": "clover_hosted",
                "name": "Clover Hosted Checkout",
                "description": "Secure payment processing with Clover",
                "type": "redirect",
                "enabled": True
            },
            {
                "id": "stripe",
                "name": "Credit/Debit Card",
                "description": "Pay with Visa, Mastercard, etc.",
                "type": "card",
                "enabled": True
            }
        ]
    })

@api_view(['POST'])
def create_checkout_session(request):
    """Create checkout session - Simple endpoint"""
    try:
        data = request.data
        payment_method = data.get('payment_method')
        order_data = data.get('order_data', {})
        card_data = data.get('card_data', {})  # Add this line
        
        # Update this condition to support both methods
        if payment_method not in ['clover_hosted', 'clover_direct']:
            return Response({
                "success": False,
                "error": "Supported payment methods: clover_hosted, clover_direct"
            }, status=status.HTTP_400_BAD_REQUEST)

        
        # Validate required fields
        required_fields = ['total_amount', 'order_number']
        for field in required_fields:
            if field not in order_data:
                return Response({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Import and initialize Clover service
        from .services import CloverPaymentService
        clover_service = CloverPaymentService()
        
        # Handle different payment methods
        if payment_method == 'clover_hosted':
            result = clover_service.create_hosted_checkout_session(order_data)
        elif payment_method == 'clover_direct':
            # Validate card data for direct payment
            required_card_fields = ['number', 'exp_month', 'exp_year', 'cvv']
            for field in required_card_fields:
                if field not in card_data:
                    return Response({
                        "success": False,
                        "error": f"Missing required card field: {field}"
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            result = clover_service.process_direct_payment(order_data, card_data)
        
        return Response({
            "is_success": result.get('success', False),
            "data": result
        })
        
    except Exception as e:
        return Response({
            "is_success": False,
            "data": {"success": False, "error": str(e)}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

'''@api_view(['POST'])
def create_clover_hosted_checkout(request):
        """
        Dedicated endpoint for Clover hosted checkout - cleaner and simpler
        """
        try:
            data = request.data
            print(f"🔍 DEBUG: Creating hosted checkout for: {data}")
            
            # Validate required fields
            if not data.get('total_amount'):
                return Response({
                    'is_success': False,
                    'data': {
                        'status': 'error',
                        'message': 'total_amount is required'
                    }
                }, status=400)
            
            # Prepare order data
            order_data = {
                'total_amount': data.get('total_amount'),
                'currency': data.get('currency', 'USD'),
                'order_number': f"HOSTED-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                'customer': data.get('customer', {}),
                'redirect_urls': {
                    'success': data.get('success_url', f"{settings.FRONTEND_URL}/checkout/success"),
                    'failure': data.get('failure_url', f"{settings.FRONTEND_URL}/checkout/failure"),
                    'cancel': data.get('cancel_url', f"{settings.FRONTEND_URL}/checkout/cancel")
                }
            }
            
            print(f"🔍 DEBUG: Prepared order data: {order_data}")
            
            # Initialize Clover service
            clover_service = CloverPaymentService()
            
            # Create hosted checkout session
            result = clover_service.create_hosted_checkout_session(order_data)
            
            if result['success']:
                return Response({
                    'is_success': True,
                    'data': {
                        'status': 'success',
                        'message': 'Hosted checkout session created successfully',
                        'checkout_url': result['checkout_url'],
                        'session_id': result['session_id'],
                        'order_id': result['order_id'],
                        'integration_type': result['integration_type'],
                        'instructions': 'Redirect user to checkout_url for payment',
                        'clover_config': result['clover_config']
                    }
                })
            else:
                return Response({
                    'is_success': False,
                    'data': {
                        'status': 'error',
                        'message': result['error']
                    }
                }, status=400)
                
        except Exception as e:
            print(f"❌ ERROR in create_clover_hosted_checkout: {str(e)}")
            return Response({
                'is_success': False,
                'data': {
                    'status': 'error',
                    'message': f'Hosted checkout creation failed: {str(e)}'
                }
            }, status=500)
'''

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
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=['GET'])
    def overview_metrics(self, request):
        """Get all dashboard overview metrics in one endpoint
        
        Query Parameters:
        - period: 'day', 'week', 'month', 'year', or 'all' (default: 'week')
        - 'all' shows metrics for all time (no date filtering)
        """
        time_period = request.query_params.get('period', 'week')
        date_threshold = self._get_date_threshold(time_period)
        previous_period_threshold = self._get_previous_period_threshold(time_period)
        
        # ABANDONED CART METRICS
        if date_threshold is None:  # All-time metrics
            total_carts_with_items = Cart.objects.filter(items__isnull=False).distinct().count()
            converted_carts = Cart.objects.filter(
                items__isnull=False,
                user__isnull=False,
                user__orders__isnull=False
            ).distinct().count()
        else:  # Time-filtered metrics
            # Get carts that have items but no completed orders from the same user after cart creation
            total_carts_with_items = Cart.objects.filter(
                created_at__gte=date_threshold,
                items__isnull=False
            ).distinct().count()
            
            # Carts that resulted in orders (not abandoned)
            converted_carts = Cart.objects.filter(
                created_at__gte=date_threshold,
                items__isnull=False,
                user__isnull=False,  # Only for logged-in users
                user__orders__created_at__gte=F('created_at'),
                user__orders__status__in=['PROCESSING', 'SHIPPED', 'DELIVERED']
            ).distinct().count()
        
        abandoned_carts = total_carts_with_items - converted_carts
        abandoned_rate = (abandoned_carts / total_carts_with_items * 100) if total_carts_with_items > 0 else 0
        
        # Previous period for comparison (only for time-filtered periods)
        if date_threshold is not None:
            prev_total_carts = Cart.objects.filter(
                created_at__gte=previous_period_threshold,
                created_at__lt=date_threshold,
                items__isnull=False
            ).distinct().count()
            
            prev_converted_carts = Cart.objects.filter(
                created_at__gte=previous_period_threshold,
                created_at__lt=date_threshold,
                items__isnull=False,
                user__isnull=False,
                user__orders__created_at__gte=F('created_at'),
                user__orders__status__in=['PROCESSING', 'SHIPPED', 'DELIVERED']
            ).distinct().count()
            
            prev_abandoned_carts = prev_total_carts - prev_converted_carts
            prev_abandoned_rate = (prev_abandoned_carts / prev_total_carts * 100) if prev_total_carts > 0 else 0
            
            abandoned_rate_change = abandoned_rate - prev_abandoned_rate
        else:
            # For all-time, set previous to 0 (no comparison)
            prev_abandoned_rate = 0
            abandoned_rate_change = 0
        
        # CUSTOMER METRICS
        if date_threshold is None:  # All-time metrics
            new_customers = CustomUser.objects.count()
            total_customers = CustomUser.objects.count()
            active_customers = CustomUser.objects.filter(orders__isnull=False).distinct().count()
        else:  # Time-filtered metrics
            # New customers this period
            new_customers = CustomUser.objects.filter(
                date_joined__gte=date_threshold
            ).count()
            
            # Total customers
            total_customers = CustomUser.objects.count()
            
            # Active customers (made an order in this period)
            active_customers = CustomUser.objects.filter(
                orders__created_at__gte=date_threshold
            ).distinct().count()
        
        # Previous period comparisons (only for time-filtered periods)
        if date_threshold is not None:
            prev_new_customers = CustomUser.objects.filter(
                date_joined__gte=previous_period_threshold,
                date_joined__lt=date_threshold
            ).count()
            
            prev_total_customers = CustomUser.objects.filter(
                date_joined__lt=date_threshold
            ).count()
            
            prev_active_customers = CustomUser.objects.filter(
                orders__created_at__gte=previous_period_threshold,
                orders__created_at__lt=date_threshold
            ).distinct().count()
        else:
            # For all-time, set previous to 0 (no comparison)
            prev_new_customers = prev_total_customers = prev_active_customers = 0
        
        # Calculate growth rates (handle all-time case)
        if date_threshold is None:
            customers_growth = total_customers_growth = active_customers_growth = 0
        else:
            customers_growth = ((new_customers - prev_new_customers) / prev_new_customers * 100) if prev_new_customers > 0 else 0
            total_customers_growth = ((total_customers - prev_total_customers) / prev_total_customers * 100) if prev_total_customers > 0 else 0
            active_customers_growth = ((active_customers - prev_active_customers) / prev_active_customers * 100) if prev_active_customers > 0 else 0
        
        # ORDER METRICS BY STATUS - COUNT ALL STATUSES
        if date_threshold is None:  # All-time metrics
            all_orders_count = Order.objects.count()
            # Count all order statuses
            pending_orders_count = Order.objects.filter(status='PENDING').count()
            processing_orders_count = Order.objects.filter(status='PROCESSING').count()
            shipped_orders_count = Order.objects.filter(status='SHIPPED').count()
            delivered_orders_count = Order.objects.filter(status='DELIVERED').count()
            cancelled_orders_count = Order.objects.filter(status='CANCELLED').count()
            returned_orders_count = Order.objects.filter(status='RETURNED').count()
            damaged_orders_count = Order.objects.filter(status='DAMAGED').count()
        else:  # Time-filtered metrics
            all_orders_count = Order.objects.filter(created_at__gte=date_threshold).count()
            # Count all order statuses within time period
            pending_orders_count = Order.objects.filter(
                created_at__gte=date_threshold,
                status='PENDING'
            ).count()
            processing_orders_count = Order.objects.filter(
                created_at__gte=date_threshold,
                status='PROCESSING'
            ).count()
            shipped_orders_count = Order.objects.filter(
                created_at__gte=date_threshold,
                status='SHIPPED'
            ).count()
            delivered_orders_count = Order.objects.filter(
                created_at__gte=date_threshold,
                status='DELIVERED'
            ).count()
            cancelled_orders_count = Order.objects.filter(
                created_at__gte=date_threshold,
                status='CANCELLED'
            ).count()
            returned_orders_count = Order.objects.filter(
                created_at__gte=date_threshold,
                status='RETURNED'
            ).count()
            damaged_orders_count = Order.objects.filter(
                created_at__gte=date_threshold,
                status='DAMAGED'
            ).count()
        
        # Previous period order counts (only for time-filtered periods)
        if date_threshold is not None:
            prev_all_orders = Order.objects.filter(
                created_at__gte=previous_period_threshold,
                created_at__lt=date_threshold
            ).count()
            prev_pending_orders = Order.objects.filter(
                created_at__gte=previous_period_threshold,
                created_at__lt=date_threshold,
                status='PENDING'
            ).count()
            prev_processing_orders = Order.objects.filter(
                created_at__gte=previous_period_threshold,
                created_at__lt=date_threshold,
                status='PROCESSING'
            ).count()
            prev_shipped_orders = Order.objects.filter(
                created_at__gte=previous_period_threshold,
                created_at__lt=date_threshold,
                status='SHIPPED'
            ).count()
            prev_delivered_orders = Order.objects.filter(
                created_at__gte=previous_period_threshold,
                created_at__lt=date_threshold,
                status='DELIVERED'
            ).count()
            prev_cancelled_orders = Order.objects.filter(
                created_at__gte=previous_period_threshold,
                created_at__lt=date_threshold,
                status='CANCELLED'
            ).count()
            prev_returned_orders = Order.objects.filter(
                created_at__gte=previous_period_threshold,
                created_at__lt=date_threshold,
                status='RETURNED'
            ).count()
            prev_damaged_orders = Order.objects.filter(
                created_at__gte=previous_period_threshold,
                created_at__lt=date_threshold,
                status='DAMAGED'
            ).count()
        else:
            # For all-time, set previous to 0 (no comparison)
            prev_all_orders = prev_pending_orders = prev_processing_orders = prev_shipped_orders = prev_delivered_orders = prev_cancelled_orders = prev_returned_orders = prev_damaged_orders = 0
        
        # Calculate order growth rates (handle all-time case)
        if date_threshold is None:
            all_orders_growth = pending_orders_growth = processing_orders_growth = shipped_orders_growth = delivered_orders_growth = cancelled_orders_growth = returned_orders_growth = damaged_orders_growth = 0
        else:
            all_orders_growth = ((all_orders_count - prev_all_orders) / prev_all_orders * 100) if prev_all_orders > 0 else 0
            pending_orders_growth = ((pending_orders_count - prev_pending_orders) / prev_pending_orders * 100) if prev_pending_orders > 0 else 0
            processing_orders_growth = ((processing_orders_count - prev_processing_orders) / prev_processing_orders * 100) if prev_processing_orders > 0 else 0
            shipped_orders_growth = ((shipped_orders_count - prev_shipped_orders) / prev_shipped_orders * 100) if prev_shipped_orders > 0 else 0
            delivered_orders_growth = ((delivered_orders_count - prev_delivered_orders) / prev_delivered_orders * 100) if prev_delivered_orders > 0 else 0
            cancelled_orders_growth = ((cancelled_orders_count - prev_cancelled_orders) / prev_cancelled_orders * 100) if prev_cancelled_orders > 0 else 0
            returned_orders_growth = ((returned_orders_count - prev_returned_orders) / prev_returned_orders * 100) if prev_returned_orders > 0 else 0
            damaged_orders_growth = ((damaged_orders_count - prev_damaged_orders) / prev_damaged_orders * 100) if prev_damaged_orders > 0 else 0
        
        return Response({
            'abandoned_cart': {
                'rate': round(abandoned_rate, 1),
                'change': round(abandoned_rate_change, 2),
                'total_carts': total_carts_with_items,
                'abandoned_count': abandoned_carts
            },
            'customers': {
                'new_customers': new_customers,
                'new_customers_growth': round(customers_growth, 1),
                'total_customers': total_customers,
                'total_growth': round(total_customers_growth, 1)
            },
            'active_customers': {
                'count': active_customers,
                'growth': round(active_customers_growth, 1)
            },
            'orders': {
                'all_orders': {
                    'count': all_orders_count,
                    'growth': round(all_orders_growth, 2)
                },
                'pending': {
                    'count': pending_orders_count,
                    'growth': round(pending_orders_growth, 2)
                },
                'processing': {
                    'count': processing_orders_count,
                    'growth': round(processing_orders_growth, 2)
                },
                'shipped': {
                    'count': shipped_orders_count,
                    'growth': round(shipped_orders_growth, 2)
                },
                'delivered': {
                    'count': delivered_orders_count,
                    'growth': round(delivered_orders_growth, 2)
                },
                'cancelled': {
                    'count': cancelled_orders_count,
                    'growth': round(cancelled_orders_growth, 2)
                },
                'returned': {
                    'count': returned_orders_count,
                    'growth': round(returned_orders_growth, 2)
                },
                'damaged': {
                    'count': damaged_orders_count,
                    'growth': round(damaged_orders_growth, 2)
                }
            },
            'period': time_period
        })
    
    @action(detail=False, methods=['GET'])
    def cart_metrics(self, request):
        """Get detailed abandoned cart metrics"""
        time_period = request.query_params.get('period', 'week')
        date_threshold = self._get_date_threshold(time_period)
        
        # Get carts with items (potential purchases)
        total_carts = Cart.objects.filter(
            created_at__gte=date_threshold,
            items__isnull=False
        ).distinct().count()
        
        # Get carts that led to actual orders
        # A cart is considered "converted" if the user made an order after creating the cart
        converted_carts = Cart.objects.filter(
            created_at__gte=date_threshold,
            items__isnull=False,
            user__isnull=False  # Only consider logged-in users for accurate tracking
        ).annotate(
            has_subsequent_order=Exists(
                Order.objects.filter(
                    user=OuterRef('user'),
                    created_at__gte=OuterRef('created_at')
                )
            )
        ).filter(has_subsequent_order=True).count()
        
        abandoned_carts = total_carts - converted_carts
        abandoned_rate = (abandoned_carts / total_carts * 100) if total_carts > 0 else 0
        
        # Get cart abandonment reasons (you might want to add this as a field to Cart model)
        abandonment_data = {
            'high_shipping_cost': 0,  # These would need additional tracking
            'payment_issues': 0,
            'just_browsing': abandoned_carts,  # Default to all abandoned
            'other': 0
        }
        
        data = {
            'abandoned_rate': round(abandoned_rate, 2),
            'total_carts': total_carts,
            'abandoned_carts': abandoned_carts,
            'converted_carts': converted_carts,
            'abandonment_reasons': abandonment_data,
            'period': time_period
        }
        
        serializer = DashboardCartMetricsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def customer_metrics(self, request):
        """Get detailed customer metrics"""
        time_period = request.query_params.get('period', 'week')
        date_threshold = self._get_date_threshold(time_period)
        previous_period_threshold = self._get_previous_period_threshold(time_period)
        
        # Current period metrics
        new_customers = CustomUser.objects.filter(date_joined__gte=date_threshold).count()
        total_customers = CustomUser.objects.count()
        active_customers = CustomUser.objects.filter(
            orders__created_at__gte=date_threshold
        ).distinct().count()
        returning_customers = CustomUser.objects.filter(
            orders__created_at__gte=date_threshold
        ).annotate(
            order_count=Count('orders')
        ).filter(order_count__gt=1).count()
        
        # Previous period for comparison
        prev_new_customers = CustomUser.objects.filter(
            date_joined__gte=previous_period_threshold,
            date_joined__lt=date_threshold
        ).count()
        
        prev_active_customers = CustomUser.objects.filter(
            orders__created_at__gte=previous_period_threshold,
            orders__created_at__lt=date_threshold
        ).distinct().count()
        
        # Calculate growth rates
        new_customer_growth = ((new_customers - prev_new_customers) / prev_new_customers * 100) if prev_new_customers > 0 else 0
        active_customer_growth = ((active_customers - prev_active_customers) / prev_active_customers * 100) if prev_active_customers > 0 else 0
        
        data = {
            'new_customers': new_customers,
            'new_customer_growth': round(new_customer_growth, 2),
            'total_customers': total_customers,
            'active_customers': active_customers,
            'active_customer_growth': round(active_customer_growth, 2),
            'returning_customers': returning_customers,
            'period': time_period
        }
        
        serializer = DashboardCustomerMetricsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def order_metrics(self, request):
        """
        Enhanced order metrics for:
        1. Order Management page filtering
        2. Sales analytics charts
        3. Detailed order breakdowns
        """
        time_period = request.query_params.get('period', 'week')
        status_filter = request.query_params.get('status', None)
        date_threshold = self._get_date_threshold(time_period)
        previous_period_threshold = self._get_previous_period_threshold(time_period)
        
        # Base queryset for current period
        if date_threshold is None:  # All-time metrics
            current_orders = Order.objects.all()
            previous_orders = Order.objects.none()  # No previous period for all-time
        else:  # Time-filtered metrics
            current_orders = Order.objects.filter(created_at__gte=date_threshold)
            previous_orders = Order.objects.filter(
                created_at__gte=previous_period_threshold,
                created_at__lt=date_threshold
            )
        
        # Apply status filter if provided (for Order Management page)
        filtered_orders = current_orders
        if status_filter and status_filter != 'all':
            filtered_orders = current_orders.filter(status=status_filter.upper())
        
        # Status breakdown for Order Management tabs
        if date_threshold is None:  # All-time metrics
            status_breakdown = Order.objects.values('status').annotate(
                count=Count('id'),
                total_value=Sum('total'),
                avg_order_value=Avg('total')
            ).order_by('status')
        else:  # Time-filtered metrics
            status_breakdown = Order.objects.filter(
                created_at__gte=date_threshold
            ).values('status').annotate(
                count=Count('id'),
                total_value=Sum('total'),
                avg_order_value=Avg('total')
            ).order_by('status')
        
        # Convert to dict for easier frontend consumption
        status_summary = {}
        total_all_orders = 0
        
        for status_data in status_breakdown:
            status = status_data['status'].lower()
            count = status_data['count']
            status_summary[status] = {
                'count': count,
                'total_value': float(status_data['total_value'] or 0),
                'avg_order_value': float(status_data['avg_order_value'] or 0)
            }
            total_all_orders += count
        
        # Add "all orders" summary
        status_summary['all'] = {
            'count': total_all_orders,
            'total_value': float(current_orders.aggregate(Sum('total'))['total__sum'] or 0),
            'avg_order_value': float(current_orders.aggregate(Avg('total'))['total__avg'] or 0)
        }
        
        # Daily trend for sales chart (last 7-30 days based on period)
        if time_period == 'all':
            # For all-time, show last 30 days trend
            trend_days = 30
        elif time_period == 'week':
            trend_days = 7
        elif time_period == 'month':
            trend_days = 30
        else:
            trend_days = 7
            
        trend_start = timezone.now().date() - timedelta(days=trend_days)
        
        daily_trend = current_orders.filter(
            created_at__date__gte=trend_start
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            revenue=Sum('total'),
            orders=Count('id')
        ).order_by('date')
        
        # Fill in missing dates with zero values
        trend_dict = {item['date']: item for item in daily_trend}
        complete_trend = []
        
        for i in range(trend_days):
            date = trend_start + timedelta(days=i)
            if date in trend_dict:
                complete_trend.append({
                    'date': date.isoformat(),
                    'revenue': float(trend_dict[date]['revenue'] or 0),
                    'orders': trend_dict[date]['orders']
                })
            else:
                complete_trend.append({
                    'date': date.isoformat(),
                    'revenue': 0.0,
                    'orders': 0
                })
        
        # Recent order activity (for management interface)
        recent_activity = filtered_orders.select_related('user', 'customer').order_by('-created_at')[:10]
        
        activity_data = []
        for order in recent_activity:
            customer_name = order.customer.name if order.customer else (
                order.user.get_full_name() if order.user else 'Unknown'
            )
            
            activity_data.append({
                'order_id': order.id,
                'order_number': order.order_number,
                'customer_name': customer_name,
                'status': order.status,
                'total': float(order.total),
                'created_at': order.created_at.isoformat(),
            })
        
        return Response({
            # For Order Management page tabs/filtering
            'status_summary': status_summary,
            
            # For sales analytics charts
            'daily_trend': complete_trend,
            'trend_period_days': trend_days,
            
            # Detailed breakdown (existing functionality)
            'status_breakdown': list(status_breakdown),
            'total_orders': filtered_orders.count(),
            'total_revenue': float(filtered_orders.aggregate(Sum('total'))['total__sum'] or 0),
            'avg_order_value': float(filtered_orders.aggregate(Avg('total'))['total__avg'] or 0),
            
            # Recent activity for management interface
            'recent_activity': activity_data,
            
            # Request parameters
            'status_filter': status_filter,
            'period': time_period,
            'date_range': {
                'start': date_threshold.isoformat() if date_threshold else None,
                'end': timezone.now().isoformat()
            }
        })

    def _get_date_threshold(self, period):
        """Helper method to get date threshold based on period"""
        now = timezone.now()
        thresholds = {
            'day': now - timedelta(days=1),
            'week': now - timedelta(weeks=1),
            'month': now - timedelta(days=30),
            'year': now - timedelta(days=365),
            'all': None  # Add support for all-time metrics
        }
        return thresholds.get(period, thresholds['week'])
    
    def _get_previous_period_threshold(self, period):
        """Helper method to get the start of previous period for comparison"""
        if period == 'all':
            return None  # No previous period for all-time metrics
            
        now = timezone.now()
        current_threshold = self._get_date_threshold(period)
        
        # Calculate the duration of current period
        duration = now - current_threshold
        
        # Previous period starts at: current_threshold - duration
        return current_threshold - duration
    
    @action(detail=False, methods=['GET'])
    def recent_orders(self, request):
        """Get recent orders for dashboard display - NEW ENDPOINT"""
        try:
            limit = int(request.query_params.get('limit', 6))
            
            # Use select_related and prefetch_related for efficiency
            recent_orders = Order.objects.select_related('user', 'customer')\
                .prefetch_related('items__product')\
                .order_by('-created_at')[:limit]
            
            orders_data = []
            for order in recent_orders:
                # Safely get first product image
                first_item = order.items.first()
                product_image = None
                first_product_name = None
                
                if first_item:
                    first_product_name = first_item.product.name
                    if hasattr(first_item.product, 'main_image') and first_item.product.main_image:
                        product_image = first_item.product.main_image.url
                
                # Use existing customer logic
                customer_name = ""
                if order.customer:
                    customer_name = order.customer.name
                elif order.user:
                    customer_name = order.user.get_full_name() or order.user.email
                
                orders_data.append({
                    'id': order.id,
                    'order_number': order.order_number,
                    'customer_name': customer_name,
                    'customer_email': order.user.email if order.user else '',
                    'total': float(order.total),  # Ensure JSON serializable
                    'status': order.status,
                    'status_display': order.get_status_display() if hasattr(order, 'get_status_display') else order.status,
                    'created_at': order.created_at.isoformat(),
                    'product_image': product_image,
                    'items_count': order.items.count(),
                    'first_product_name': first_product_name
                })
            
            return Response({
                'recent_orders': orders_data,
                'total_count': Order.objects.count(),
                'period': 'all'  # Indicate this shows all orders, not time-filtered
            })
            
        except Exception as e:
            # Graceful error handling
            return Response({
                'recent_orders': [],
                'total_count': 0,
                'error': 'Failed to fetch recent orders'
            }, status=500)
        
    @action(detail=False, methods=['GET'])
    def product_management_data(self, request):
            """
            Enhanced endpoint for Product Management page data
            Matches the table interface in your screenshot
            """
            # Get filter parameters
            tab = request.query_params.get('tab', 'all')
            search = request.query_params.get('search', '')
            category = request.query_params.get('category', '')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # Base queryset
            queryset = Product.objects.select_related('category').prefetch_related('variations')
            
            # Apply tab filtering
            if tab == 'published':
                queryset = queryset.filter(status='published')
            elif tab == 'low_stock':
                queryset = queryset.filter(stock_quantity__lte=10)
            elif tab == 'draft':
                queryset = queryset.filter(status='draft')
            
            # Apply search
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) | 
                    Q(sku__icontains=search) |
                    Q(category__name__icontains=search)
                )
            
            # Apply category filter
            if category:
                queryset = queryset.filter(category__slug=category)
            
            # Get total count for pagination
            total_count = queryset.count()
            
            # Apply pagination
            start = (page - 1) * page_size
            end = start + page_size
            products = queryset[start:end]
            
            # Serialize product data to match your table structure
            product_data = []
            for product in products:
                # Get variant count
                variant_count = product.variations.count()
                
                # Get stock status
                if product.stock_quantity == 0:
                    stock_status = 'out_of_stock'
                    stock_label = 'Out of Stock'
                    stock_color = 'red'
                elif product.stock_quantity <= 10:
                    stock_status = 'low_stock'
                    stock_label = 'Low Stock'
                    stock_color = 'orange'
                else:
                    stock_status = 'in_stock'
                    stock_label = 'In Stock'
                    stock_color = 'green'
                
                # Get status display
                status_colors = {
                    'published': 'green',
                    'draft': 'gray',
                    'active': 'blue',
                    'inactive': 'red'
                }
                
                product_data.append({
                    'id': product.id,
                    'name': product.name,
                    'sku': product.sku,
                    'category': product.category.name if product.category else 'Uncategorized',
                    'category_id': product.category.id if product.category else None,
                    'variants': f"{variant_count} Variants" if variant_count > 0 else "No Variants",
                    'variant_count': variant_count,
                    'stock_quantity': product.stock_quantity,
                    'stock_status': stock_status,
                    'stock_label': stock_label,
                    'stock_color': stock_color,
                    'price': float(product.price),
                    'status': product.status,
                    'status_color': status_colors.get(product.status, 'gray'),
                    'created_at': product.created_at.strftime('%d %b %Y'),
                    'updated_at': product.updated_at.strftime('%d %b %Y'),
                    'main_image': product.main_image.url if product.main_image else None,
                    'is_featured': product.is_featured,
                    'rating': float(product.rating) if product.rating else 0,
                    'num_ratings': product.num_ratings
                })
            
            # Calculate pagination info
            total_pages = (total_count + page_size - 1) // page_size
            
            return Response({
                'products': product_data,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_count': total_count,
                    'page_size': page_size,
                    'has_next': page < total_pages,
                    'has_previous': page > 1
                },
                'filters': {
                    'tab': tab,
                    'search': search,
                    'category': category
                },
                'tab_counts': {
                    'all': Product.objects.count(),
                    'published': Product.objects.filter(status='published').count(),
                    'low_stock': Product.objects.filter(stock_quantity__lte=10).count(),
                    'draft': Product.objects.filter(status='draft').count()
                }
            })
        
    @action(detail=False, methods=['POST'])
    def bulk_product_action(self, request):
        """
        Handle bulk actions on products (delete, change status, etc.)
        """
        action = request.data.get('action')
        product_ids = request.data.get('product_ids', [])
        
        if not action or not product_ids:
            return Response({
                'error': 'Action and product_ids are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        products = Product.objects.filter(id__in=product_ids)
        
        if action == 'delete':
            deleted_count = products.count()
            products.delete()
            return Response({
                'message': f'{deleted_count} products deleted successfully'
            })
        
        elif action == 'publish':
            updated_count = products.update(status='published')
            return Response({
                'message': f'{updated_count} products published successfully'
            })
        
        elif action == 'draft':
            updated_count = products.update(status='draft')
            return Response({
                'message': f'{updated_count} products moved to draft'
            })
        
        elif action == 'feature':
            updated_count = products.update(is_featured=True)
            return Response({
                'message': f'{updated_count} products marked as featured'
            })
        
        else:
            return Response({
                'error': 'Invalid action'
            }, status=400)
    
    @action(detail=False, methods=['GET'])
    def export_products(self, request):
        """
        Export products data as CSV
        """
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="products.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Name', 'SKU', 'Category', 'Price', 'Stock', 'Status', 'Created'
        ])
        
        products = Product.objects.select_related('category').all()
        for product in products:
            writer.writerow([
                product.name,
                product.sku,
                product.category.name if product.category else '',
                product.price,
                product.stock_quantity,
                product.status,
                product.created_at.strftime('%Y-%m-%d')
            ])
        
        return response

    @action(detail=False, methods=['GET'])
    def dashboard_summary(self, request):
        """
        Consolidated dashboard summary - SAFE VERSION
        This complements your existing overview_metrics without replacing it
        
        Query Parameters:
        - period: 'day', 'week', 'month', 'year', or 'all' (default: 'week')
        - 'all' shows metrics for all time (no date filtering)
        """
        try:
            time_period = request.query_params.get('period', 'week')
            date_threshold = self._get_date_threshold(time_period)
            
            # Basic counts (safe queries) - COUNT ALL ORDER STATUSES
            if date_threshold is None:  # All-time metrics
                total_orders = Order.objects.count()
                pending_orders = Order.objects.filter(status='PENDING').count()
                processing_orders = Order.objects.filter(status='PROCESSING').count()
                shipped_orders = Order.objects.filter(status='SHIPPED').count()
                delivered_orders = Order.objects.filter(status='DELIVERED').count()
                cancelled_orders = Order.objects.filter(status='CANCELLED').count()
                returned_orders = Order.objects.filter(status='RETURNED').count()
                damaged_orders = Order.objects.filter(status='DAMAGED').count()
                
                # Revenue calculation with error handling
                revenue_data = Order.objects.aggregate(total_revenue=Sum('total'))
            else:  # Time-filtered metrics
                total_orders = Order.objects.filter(created_at__gte=date_threshold).count()
                pending_orders = Order.objects.filter(
                    created_at__gte=date_threshold, 
                    status='PENDING'
                ).count()
                processing_orders = Order.objects.filter(
                    created_at__gte=date_threshold, 
                    status='PROCESSING'
                ).count()
                shipped_orders = Order.objects.filter(
                    created_at__gte=date_threshold, 
                    status='SHIPPED'
                ).count()
                delivered_orders = Order.objects.filter(
                    created_at__gte=date_threshold, 
                    status='DELIVERED'
                ).count()
                cancelled_orders = Order.objects.filter(
                    created_at__gte=date_threshold, 
                    status='CANCELLED'
                ).count()
                returned_orders = Order.objects.filter(
                    created_at__gte=date_threshold, 
                    status='RETURNED'
                ).count()
                damaged_orders = Order.objects.filter(
                    created_at__gte=date_threshold, 
                    status='DAMAGED'
                ).count()
                
                # Revenue calculation with error handling
                revenue_data = Order.objects.filter(
                    created_at__gte=date_threshold
                ).aggregate(total_revenue=Sum('total'))
            
            total_revenue = revenue_data['total_revenue'] or 0
            
            # Get unread notification count
            from .models import OrderNotification
            unread_notifications = OrderNotification.objects.filter(is_read=False).count()
            
            return Response({
                'summary': {
                    'all_orders': {
                        'count': total_orders,
                        'label': 'All Orders'
                    },
                    'pending_orders': {
                        'count': pending_orders,
                        'label': 'Pending'
                    },
                    'processing_orders': {
                        'count': processing_orders,
                        'label': 'Processing'
                    },
                    'shipped_orders': {
                        'count': shipped_orders,
                        'label': 'Shipped'
                    },
                    'delivered_orders': {
                        'count': delivered_orders,
                        'label': 'Delivered'
                    },
                    'cancelled_orders': {
                        'count': cancelled_orders,
                        'label': 'Cancelled'
                    },
                    'returned_orders': {
                        'count': returned_orders,
                        'label': 'Returned'
                    },
                    'damaged_orders': {
                        'count': damaged_orders,
                        'label': 'Damaged'
                    },
                    'total_revenue': float(total_revenue)
                },
                'notifications': {
                    'unread_count': unread_notifications
                },
                'period': time_period,
                'last_updated': timezone.now().isoformat()
            })
            
        except Exception as e:
            # Return safe defaults on error
            return Response({
                'summary': {
                    'all_orders': {'count': 0, 'label': 'All Orders'},
                    'pending_orders': {'count': 0, 'label': 'Pending'},
                    'processing_orders': {'count': 0, 'label': 'Processing'},
                    'shipped_orders': {'count': 0, 'label': 'Shipped'},
                    'delivered_orders': {'count': 0, 'label': 'Delivered'},
                    'cancelled_orders': {'count': 0, 'label': 'Cancelled'},
                    'returned_orders': {'count': 0, 'label': 'Returned'},
                    'damaged_orders': {'count': 0, 'label': 'Damaged'},
                    'total_revenue': 0
                },
                'period': time_period,
                'error': 'Failed to fetch summary data'
            })

    # SAFE HELPER METHOD - Add this to your DashboardViewSet
    def _safe_get_order_status_display(self, status):
        """
        Safe status display mapping without changing existing logic
        """
        ui_status_mapping = {
            'PENDING': 'Pending',
            'PROCESSING': 'Processing', 
            'SHIPPED': 'Shipped',
            'DELIVERED': 'Completed',  # Map to UI expectation
            'CANCELLED': 'Cancelled',
            # Add fallbacks for any other statuses
            'COMPLETED': 'Completed',
            'Completed': 'Completed'
        }
        return ui_status_mapping.get(status, status)
    

    # OPTIONAL: Enhanced version of your existing overview_metrics
    # Only add this if you want to enhance the existing endpoint
    def _enhance_overview_response(self, response_data):
        
        # Add UI-friendly status displays
        if 'orders' in response_data:
            orders = response_data['orders']
            if 'completed' in orders:
                orders['completed']['label'] = 'Completed'
            if 'pending' in orders:
                orders['pending']['label'] = 'Pending'
            if 'all_orders' in orders:
                orders['all_orders']['label'] = 'All Orders'
        
        # Add timestamp
        response_data['last_updated'] = timezone.now().isoformat()
        
        return response_data

    @action(detail=False, methods=['GET'], url_path='summary-chart-data')
    def summary_chart_data(self, request):
        metric = request.query_params.get('metric', 'sales')
        period = request.query_params.get('period', 'last_7_days') # e.g., last_7_days, last_30_days, this_month

        today = timezone.now().date()
        data_points = []
        queryset = None
        annotation_value = None
        period_label = ""

        # Determine date range and grouping
        if period == 'last_7_days':
            start_date = today - timedelta(days=6)
            end_date = today
            trunc_func = TruncDay
            period_label = "Last 7 Days"
        elif period == 'last_30_days':
            start_date = today - timedelta(days=29)
            end_date = today
            trunc_func = TruncDay # Could also be TruncWeek if preferred for longer periods
            period_label = "Last 30 Days"
        elif period == 'this_month':
            start_date = today.replace(day=1)
            end_date = today
            trunc_func = TruncDay
            period_label = "This Month"
        # Add more periods like 'last_month', 'this_year' as needed
        else:
            # Default to last 7 days if period is invalid
            start_date = today - timedelta(days=6)
            end_date = today
            trunc_func = TruncDay
            period_label = "Last 7 Days"

        # Metric specific logic
        metric_label = ""
        if metric == 'sales':
            queryset = Order.objects.filter(created_at__date__range=[start_date, end_date])
            annotation_value = Sum('total')
            metric_label = "Total Sales"
        elif metric == 'orders_count':
            queryset = Order.objects.filter(created_at__date__range=[start_date, end_date])
            annotation_value = Count('id')
            metric_label = "Total Orders"
        elif metric == 'new_customers_count':
            queryset = CustomUser.objects.filter(date_joined__date__range=[start_date, end_date])
            annotation_value = Count('id')
            metric_label = "New Customers"
        else:
            return Response({"error": "Invalid metric specified. Choose from 'sales', 'orders_count', 'new_customers_count'."},
                            status=status.HTTP_400_BAD_REQUEST)

        if queryset is not None and annotation_value is not None:
            # Group by the truncated date and annotate
            # For CustomUser, the date field is date_joined, for Order it's created_at
            date_field_name = 'date_joined__date' if metric == 'new_customers_count' else 'created_at__date'
            
            # Ensure correct date field for truncation
            trunc_date_field = 'date_joined' if metric == 'new_customers_count' else 'created_at'

            summary = queryset.annotate(
                date_period=trunc_func(trunc_date_field)
            ).values('date_period').annotate(
                metric_value=Coalesce(annotation_value, Value(0, output_field=DecimalField() if metric == 'sales' else models.IntegerField()))
            ).order_by('date_period')
            
            # Fill in missing dates with zero values for a continuous chart
            # Create a dictionary of existing data points
            summary_dict = {item['date_period'].strftime('%Y-%m-%d'): item['metric_value'] for item in summary}

            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                value = summary_dict.get(date_str, Decimal('0.00') if metric == 'sales' else 0)
                data_points.append({'date': current_date, 'value': value})
                current_date += timedelta(days=1)
        
        serializer = SummaryChartResponseSerializer(data={
            'chart_data': data_points,
            'metric_label': metric_label,
            'period_label': period_label
        })
        serializer.is_valid(raise_exception=True) # Should always be valid if data is prepared correctly
        return Response(serializer.data)

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
    """
    ViewSet for managing product sizes
    """
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']

    @action(detail=False, methods=['GET'])
    def usage_count(self, request):
        """Get count of products using each size"""
        sizes = self.get_queryset().annotate(
            product_count=Count('variations__product', distinct=True)
        )
        data = [{'id': size.id, 'name': size.name, 'product_count': size.product_count} for size in sizes]
        return Response(data)

    @action(detail=False, methods=['POST'])
    def bulk_create(self, request):
        """Bulk create multiple sizes"""
        size_names = request.data.get('names', [])
        if not size_names:
            return Response({'error': 'names array is required'}, status=400)
        
        created_sizes = []
        errors = []
        
        for name in size_names:
            try:
                size, created = Size.objects.get_or_create(name=name.strip())
                if created:
                    created_sizes.append({'name': size.name, 'id': size.id})
                else:
                    errors.append(f"Size '{name}' already exists")
            except Exception as e:
                errors.append(f"Error creating size '{name}': {str(e)}")
        
        return Response({
            'message': f'Successfully created {len(created_sizes)} sizes',
            'created_sizes': created_sizes,
            'errors': errors if errors else None
        })


class ColorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product colors
    """
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'hex_code']
    ordering_fields = ['name']
    ordering = ['name']

    @action(detail=False, methods=['GET'])
    def usage_count(self, request):
        """Get count of products using each color"""
        colors = self.get_queryset().annotate(
            product_count=Count('variations__product', distinct=True)
        )
        data = [{'id': color.id, 'name': color.name, 'hex_code': color.hex_code, 'product_count': color.product_count} for color in colors]
        return Response(data)

    @action(detail=False, methods=['POST'])
    def bulk_create(self, request):
        """Bulk create multiple colors"""
        color_data = request.data.get('colors', [])
        if not color_data:
            return Response({'error': 'colors array is required'}, status=400)
        
        created_colors = []
        errors = []
        
        for color_info in color_data:
            try:
                name = color_info.get('name', '').strip()
                hex_code = color_info.get('hex_code', '').strip()
                
                if not name:
                    errors.append("Color name is required")
                    continue
                
                color, created = Color.objects.get_or_create(
                    name=name,
                    defaults={'hex_code': hex_code} if hex_code else {}
                )
                
                if created:
                    created_colors.append({'name': color.name, 'hex_code': color.hex_code, 'id': color.id})
                else:
                    errors.append(f"Color '{name}' already exists")
                    
            except Exception as e:
                errors.append(f"Error creating color '{color_info}': {str(e)}")
        
        return Response({
            'message': f'Successfully created {len(created_colors)} colors',
            'created_colors': created_colors,
            'errors': errors if errors else None
        })

    @action(detail=False, methods=['GET'])
    def color_palette(self, request):
        """Get colors organized by hex code for color picker"""
        colors = self.get_queryset().exclude(hex_code__isnull=True).exclude(hex_code='')
        data = [{'id': color.id, 'name': color.name, 'hex_code': color.hex_code} for color in colors]
        return Response(data)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductManagementSerializer
    filterset_class = ProductFilter
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    authentication_classes = [JWTAuthentication, TokenAuthentication, SessionAuthentication]  # Add authentication
    #permission_classes = [AllowAny]  # Allow anyone to view products but the auth context will be used for wishlist
    search_fields = ['name', 'description', 'category__name']
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_permissions(self):
        """
        Override permissions:
        - Admin access required for management operations
        - Public access for read-only operations
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 
                        'bulk_update_status', 'update_status', 'export',
                        'upload_image', 'remove_image', 'upload_images',
                        'remove_images', 'add_sizes', 'add_colors',
                        'remove_size', 'remove_color']:
            return [IsAdminUser()]
        return [AllowAny()]

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

    def update(self, request, *args, **kwargs):
        """Custom update method to handle file uploads and grouped variations properly"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        import json
        
        # Extract raw variations payload for detection/parsing
        raw_variations = request.data.get('variations', None)
        
        # Determine if client sent the new grouped-by-size format
        is_grouped_map = False
        grouped_variations_map = None
        
        if isinstance(raw_variations, dict):
            is_grouped_map = True
            grouped_variations_map = raw_variations
        elif isinstance(raw_variations, str):
            # Attempt to parse JSON string maps
            try:
                parsed = json.loads(raw_variations)
                if isinstance(parsed, dict):
                    is_grouped_map = True
                    grouped_variations_map = parsed
            except Exception:
                pass
        
        # Prepare data for serializer (remove grouped map and normalize fields)
        data = request.data.copy()
        if is_grouped_map:
            data.pop('variations', None)
        
        # Combine request.data and request.FILES for the serializer
        if request.FILES:
            # Only add files that aren't already in data to avoid duplication
            for key, file_list in request.FILES.items():
                if key not in data:
                    data[key] = file_list
                else:
                    # If key exists in both, prefer the file from FILES
                    data[key] = file_list
        
        serializer = self.get_serializer(instance, data=data, partial=partial)
        
        if serializer.is_valid():
            product = serializer.save()
            
            # If grouped format is provided, create variations accordingly
            if is_grouped_map and grouped_variations_map:
                # Lazily import models used below
                from .models import ProductVariation, Size, Color
                base_price = float(product.price) if product.price is not None else 0.0
                
                # Clear existing variations
                product.variations.all().delete()
                
                for size_name, payload in grouped_variations_map.items():
                    if not isinstance(payload, dict):
                        continue
                    
                    size_id = payload.get('size_id')
                    colors_input = payload.get('colors', [])
                    price_value = payload.get('price', base_price)
                    stock_quantity = payload.get('stock_quantity', 0)
                    
                    # Resolve Size: prefer size name for new variations; fallback to size_id
                    size_obj = None
                    if size_name:
                        # First try to get or create by name (this allows custom size names)
                        size_obj, _ = Size.objects.get_or_create(name=size_name)
                    elif size_id:
                        # Fallback to size_id if no name provided
                        try:
                            size_obj = Size.objects.get(id=size_id)
                        except Size.DoesNotExist:
                            size_obj = None
                    
                    # Resolve Colors: accept list of names or ids; create by name if needed
                    color_objs = []
                    for c in colors_input:
                        if isinstance(c, int):
                            try:
                                color_objs.append(Color.objects.get(id=c))
                            except Color.DoesNotExist:
                                pass
                        else:
                            # Treat as name/string
                            name = str(c).strip()
                            if name:
                                color_obj, _ = Color.objects.get_or_create(name=name)
                                color_objs.append(color_obj)
                    
                    # Compute price adjustment vs base product price
                    try:
                        price_adj = float(price_value) - base_price
                    except Exception:
                        price_adj = 0.0
                    
                    # Create the variation row
                    variation = ProductVariation.objects.create(
                        product=product,
                        variation_type='size',
                        variation=size_name or '',
                        price_adjustment=price_adj,
                        stock_quantity=stock_quantity,
                        is_default=False,
                    )
                    
                    # Link size and colors via M2M and legacy FK for compatibility
                    if size_obj is not None:
                        variation.sizes.add(size_obj)
                        variation.size = size_obj  # legacy FK field
                    if color_objs:
                        variation.colors.set(color_objs)
                        # For legacy FK, set the first color if not already set
                        if variation.color_id is None:
                            variation.color = color_objs[0]
                    
                    # Auto-generate SKU if absent
                    if not variation.sku:
                        variation.sku = variation.generate_sku()
                    variation.save()
            
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        """Automatically generate SKU when creating a product"""
        from .utils import generate_sku
        
        # Get the product instance before saving
        product = serializer.save()
        
        # Generate SKU if not provided
        if not product.sku:
            category = product.category
            sku = generate_sku(product.name, category, product.sku)
            product.sku = sku
            product.save(update_fields=['sku'])
            print(f"✅ Generated SKU '{sku}' for product '{product.name}'")
        
        return product

    @action(detail=False, methods=['POST'])
    def regenerate_skus(self, request):
        """Regenerate SKUs for all products that don't have them"""
        from .utils import generate_sku
        
        products_without_sku = Product.objects.filter(sku__isnull=True) | Product.objects.filter(sku='')
        updated_count = 0
        
        for product in products_without_sku:
            try:
                old_sku = product.sku
                product.sku = generate_sku(product.name, product.category, product.sku)
                product.save(update_fields=['sku'])
                updated_count += 1
                print(f"✅ Regenerated SKU for '{product.name}': {old_sku} → {product.sku}")
            except Exception as e:
                print(f"❌ Error regenerating SKU for '{product.name}': {e}")
        
        return Response({
            'status': 'success',
            'message': f'Successfully regenerated SKUs for {updated_count} products',
            'updated_count': updated_count
        })

    @action(detail=True, methods=['POST'])
    def regenerate_sku(self, request, pk=None):
        """Regenerate SKU for a specific product"""
        from .utils import generate_sku
        
        product = self.get_object()
        old_sku = product.sku
        
        try:
            product.sku = generate_sku(product.name, product.category, product.sku)
            product.save(update_fields=['sku'])
            
            return Response({
                'status': 'success',
                'message': f'Successfully regenerated SKU for {product.name}',
                'old_sku': old_sku,
                'new_sku': product.sku
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error regenerating SKU: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['GET'])
    def check_sku_uniqueness(self, request):
        """Check SKU uniqueness across all products"""
        from .utils import is_sku_unique
        
        sku = request.query_params.get('sku')
        if not sku:
            return Response({
                'status': 'error',
                'message': 'SKU parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        is_unique = is_sku_unique(sku)
        
        return Response({
            'status': 'success',
            'sku': sku,
            'is_unique': is_unique,
            'message': f"SKU '{sku}' is {'unique' if is_unique else 'already in use'}"
        })

    @action(detail=True, methods=['POST'])
    def regenerate_variation_skus(self, request, pk=None):
        """Regenerate SKUs for all variations of a specific product"""
        product = self.get_object()
        variations = product.variations.all()
        
        updated_count = 0
        updated_skus = []
        
        for variation in variations:
            try:
                old_sku = variation.sku
                variation.sku = variation.generate_sku()
                variation.save(update_fields=['sku'])
                updated_count += 1
                updated_skus.append({
                    'variation_id': variation.id,
                    'old_sku': old_sku,
                    'new_sku': variation.sku
                })
            except Exception as e:
                return Response({
                    'status': 'error',
                    'message': f'Error updating variation {variation.id}: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'status': 'success',
            'message': f'Successfully regenerated SKUs for {updated_count} variations of {product.name}',
            'updated_count': updated_count,
            'updated_skus': updated_skus
        })

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
        """Create a product.

        Supports two variation input formats without breaking existing behavior:
        1) Existing array format handled by ProductManagementSerializer (unchanged)
        2) New grouped-by-size map, e.g.
           {
             "variations": {
               "Small": {"size_id": 1, "colors": ["Red","Blue"], "price": 40.0, "stock_quantity": 100},
               ...
             }
           }

        When the grouped format is provided, we parse and create variations after
        creating the product, leaving the serializer's native array handling intact
        for the legacy format.
        """

        import json

        # Extract raw variations payload for detection/parsing
        raw_variations = request.data.get('variations', None)

        # Determine if client sent the new grouped-by-size format
        is_grouped_map = False
        grouped_variations_map = None

        if isinstance(raw_variations, dict):
            is_grouped_map = True
            grouped_variations_map = raw_variations
        elif isinstance(raw_variations, str):
            # Attempt to parse JSON string maps
            try:
                parsed = json.loads(raw_variations)
                if isinstance(parsed, dict):
                    is_grouped_map = True
                    grouped_variations_map = parsed
            except Exception:
                pass

        # Prepare data for serializer (remove grouped map and normalize fields)
        data_for_serializer = request.data.copy()
        if is_grouped_map:
            data_for_serializer.pop('variations', None)
        # Normalize blank SKU to omission so auto-generation can occur safely
        try:
            if 'sku' in data_for_serializer and str(data_for_serializer.get('sku', '')).strip() == '':
                data_for_serializer.pop('sku', None)
        except Exception:
            pass
        # Normalize blank slug to omission so auto-generation can occur safely
        try:
            if 'slug' in data_for_serializer and str(data_for_serializer.get('slug', '')).strip() == '':
                data_for_serializer.pop('slug', None)
        except Exception:
            pass

        # Resolve category if provided by name (accept either ID or name). Auto-create if admin.
        try:
            if 'category' in data_for_serializer:
                from .models import Category
                raw_cat = data_for_serializer.get('category')
                if isinstance(raw_cat, str) and raw_cat.strip() != '':
                    # Numeric string treated as id
                    if raw_cat.isdigit():
                        data_for_serializer['category'] = int(raw_cat)
                    else:
                        # Treat as name; try resolve by name (case-insensitive)
                        name_query = raw_cat.strip()
                        cat_obj = Category.objects.filter(name__iexact=name_query).first()
                        if not cat_obj:
                            # If admin, auto-create with generated slug
                            user = getattr(request, 'user', None)
                            if user and user.is_staff:
                                from django.utils.text import slugify
                                base_slug = slugify(name_query) or 'category'
                                unique_slug = base_slug
                                counter = 1
                                while Category.objects.filter(slug=unique_slug).exists():
                                    unique_slug = f"{base_slug}-{counter}"
                                    counter += 1
                                cat_obj = Category.objects.create(name=name_query, slug=unique_slug)
                            else:
                                # Non-admin cannot auto-create by name; leave as-is so serializer errors clearly
                                pass
                        if cat_obj:
                            data_for_serializer['category'] = cat_obj.id
                elif isinstance(raw_cat, int):
                    # already an id
                    pass
        except Exception:
            # Do not block creation due to category resolution errors; serializer will validate
            pass

        # Create product using existing serializer behavior
        # Only mark as handled if we actually have files to handle
        has_files = hasattr(self.request, 'FILES') and (
            self.request.FILES.get('main_image_file') or 
            self.request.FILES.getlist('image_files')
        )
        serializer = self.get_serializer(
            data=data_for_serializer,
            context={**self.get_serializer_context(), 'handled_image_files': has_files}
        )
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        # Handle initial images from multipart form-data (optional)
        try:
            main_image_file = None
            if hasattr(self.request, 'FILES'):
                # main image
                main_image_file = self.request.FILES.get('main_image')
                if main_image_file:
                    try:
                        from cloudinary.uploader import upload as cloudinary_upload
                        result = cloudinary_upload(
                            main_image_file,
                            folder='products/',
                            resource_type='image'
                        )
                        url = result.get('secure_url') or result.get('url')
                        if url:
                            product.main_image = url
                            product.save(update_fields=['main_image'])
                    except Exception:
                        # If cloudinary upload fails, skip main image
                        pass

                # additional gallery images
                additional_files = []
                try:
                    additional_files = self.request.FILES.getlist('image_files') or []
                except Exception:
                    additional_files = []
                if additional_files:
                    # Upload to Cloudinary and append URLs to images JSON field
                    try:
                        from cloudinary.uploader import upload as cloudinary_upload
                        current_images = product.images or []
                        for file_obj in additional_files:
                            try:
                                result = cloudinary_upload(
                                    file_obj,
                                    folder=f'products/{product.id}/',
                                    resource_type='image'
                                )
                                url = result.get('secure_url') or result.get('url')
                                if url:
                                    current_images.append(url)
                            except Exception:
                                # Skip individual failed uploads without breaking creation
                                continue
                        product.images = current_images
                        
                        # Auto-set first image as main_image ONLY if no main_image_file was provided
                        if not main_image_file and not product.main_image and current_images:
                            # Use the first uploaded image URL as main_image
                            product.main_image = current_images[0]
                        
                        product.save(update_fields=['images', 'main_image'])
                    except Exception:
                        # If cloudinary isn't available or any unexpected issue, keep proceeding
                        pass
        except Exception:
            # Never fail product creation due to image handling
            pass

        # If grouped format is provided, create variations accordingly
        if is_grouped_map and grouped_variations_map:
            # Lazily import models used below
            from .models import ProductVariation, Size, Color
            base_price = float(product.price) if product.price is not None else 0.0

            for size_name, payload in grouped_variations_map.items():
                if not isinstance(payload, dict):
                    continue

                size_id = payload.get('size_id')
                colors_input = payload.get('colors', [])
                price_value = payload.get('price', base_price)
                stock_quantity = payload.get('stock_quantity', 0)

                # Resolve Size: prefer size_name for custom sizes; fallback to size_id
                size_obj = None
                if size_name:
                    # Try to get or create by name first (for custom sizes like XXL, Standard)
                    size_obj, _ = Size.objects.get_or_create(name=size_name)
                elif size_id:
                    # Fallback to size_id if no size_name provided
                    try:
                        size_obj = Size.objects.get(id=size_id)
                    except Size.DoesNotExist:
                        size_obj = None

                # Resolve Colors: accept list of names or ids; create by name if needed
                color_objs = []
                for c in colors_input:
                    if isinstance(c, int):
                        try:
                            color_objs.append(Color.objects.get(id=c))
                        except Color.DoesNotExist:
                            pass
                    else:
                        # Treat as name/string
                        name = str(c).strip()
                        if name:
                            color_obj, _ = Color.objects.get_or_create(name=name)
                            color_objs.append(color_obj)

                # Compute price adjustment vs base product price
                try:
                    price_adj = float(price_value) - base_price
                except Exception:
                    price_adj = 0.0

                # Create the variation row
                variation = ProductVariation.objects.create(
                    product=product,
                    variation_type='size',
                    variation=size_name or '',
                    price_adjustment=price_adj,
                    stock_quantity=stock_quantity,
                    is_default=False,
                )

                # Link size and colors via M2M and legacy FK for compatibility
                if size_obj is not None:
                    variation.sizes.add(size_obj)
                    variation.size = size_obj  # legacy FK field
                if color_objs:
                    variation.colors.set(color_objs)
                    # For legacy FK, set the first color if not already set
                    if variation.color_id is None:
                        variation.color = color_objs[0]

                # Auto-generate SKU if absent
                if not variation.sku:
                    variation.sku = variation.generate_sku()
                variation.save()

        # Build response: keep serializer output and include grouped variations map
        response_data = serializer.data

        # Always include grouped variations in the response for frontend alignment
        try:
            # Construct grouped map with color names (as per attached expected structure)
            grouped = {}
            qs = product.variations.prefetch_related('sizes', 'colors')
            base_price_resp = float(product.price) if product.price is not None else 0.0
            for var in qs:
                for s in var.sizes.all():
                    size_key = s.name
                    if size_key not in grouped:
                        grouped[size_key] = {
                            'size_id': s.id,
                            'colors': [],
                            'price': float(base_price_resp + (var.price_adjustment or 0)),
                            'stock_quantity': var.stock_quantity,
                        }
                    # Append color names
                    for col in var.colors.all():
                        if col.name not in grouped[size_key]['colors']:
                            grouped[size_key]['colors'].append(col.name)

            response_data = {
                **response_data,
                'variations': grouped,
            }
        except Exception:
            # On any unexpected issue, still return the base serializer data
            pass

        return Response(response_data, status=status.HTTP_201_CREATED)

    # Removed conflicting update method - using serializer's update method instead
    
    @action(detail=True, methods=['POST'])
    def duplicate(self, request, pk=None):
        """
        Duplicate a product
        """
        try:
            original_product = self.get_object()
            
            # Create duplicate
            duplicate_product = Product.objects.create(
                name=f"{original_product.name} (Copy)",
                description=original_product.description,
                price=original_product.price,
                stock_quantity=0,  # Start with 0 stock
                category=original_product.category,
                status='draft',  # Start as draft
                is_physical_product=original_product.is_physical_product,
                weight=original_product.weight,
                height=original_product.height,
                length=original_product.length,
                width=original_product.width,
                product_details=original_product.product_details,
                # Generate new SKU
                sku=f"{original_product.sku}-COPY-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            )
            
            # Copy variations
            for variation in original_product.variations.all():
                new_variation = ProductVariation.objects.create(
                    product=duplicate_product,
                    variation_type=variation.variation_type,
                    variation=variation.variation,
                    price_adjustment=variation.price_adjustment,
                    stock_quantity=0,
                    sku=f"{variation.sku}-COPY-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                    size=variation.size,
                    color=variation.color
                )
                # Copy ManyToMany relationships
                new_variation.sizes.set(variation.sizes.all())
                new_variation.colors.set(variation.colors.all())
            
            return Response({
                'message': 'Product duplicated successfully',
                'product_id': duplicate_product.id
            })
            
        except Exception as e:
            return Response({
                'error': f'Failed to duplicate product: {str(e)}'
            }, status=500)
    
    @action(detail=True, methods=['POST'])
    def update_stock(self, request, pk=None):
        """
        Quick stock update
        """
        product = self.get_object()
        new_stock = request.data.get('stock_quantity')
        
        if new_stock is not None:
            product.stock_quantity = new_stock
            product.save()
            
            return Response({
                'message': 'Stock updated successfully',
                'new_stock': product.stock_quantity
            })
        
        return Response({
            'error': 'stock_quantity is required'
        }, status=400)
    
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
        
        try:
            from cloudinary.uploader import upload as cloudinary_upload
            
            # Upload to Cloudinary
            result = cloudinary_upload(
                image,
                folder='products/',
                resource_type='image'
            )
            
            image_url = result.get('secure_url') or result.get('url')
            
            if image_type == 'main':
                # Handle main image
                if product.main_image:
                    try:
                        product.main_image.delete()
                    except Exception:
                        pass  # Continue even if deletion fails
                product.main_image = image_url
            else:
                # Handle additional images
                current_images = product.images or []
                current_images.append(image_url)
                product.images = current_images
                
            product.save()
            return Response({
                'message': 'Image uploaded successfully',
                'image_url': image_url,
                'type': image_type
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to upload image: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Compatibility route to avoid hyphen/underscore mapping issues in some setups
    @action(detail=True, methods=['POST'], url_path='upload_image')
    def upload_image_underscore(self, request, pk=None):
        return self.upload_image(request, pk)

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
                upload_result = cloudinary_upload(
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

    # Compatibility route for underscore variant
    @action(detail=True, methods=['POST'], url_path='upload_images')
    def upload_images_underscore(self, request, pk=None):
        return self.upload_images(request, pk)
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

    def destroy(self, request, *args, **kwargs):
        """Custom destroy method to return proper response format"""
        try:
            instance = self.get_object()
            instance.delete()
            return Response({
                'is_success': True,
                'message': 'Product deleted successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'is_success': False,
                'message': f'Error deleting product: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

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
    queryset = CarouselItem.objects.all().order_by('order')
    serializer_class = CarouselItemSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    authentication_classes = [JWTAuthentication, TokenAuthentication, SessionAuthentication]

    def get_permissions(self):
        if self.action == 'public':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.action == 'public':
            return CarouselItemPublicSerializer
        return CarouselItemSerializer

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def public(self, request):
        limit = int(request.query_params.get('limit', 5))
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

class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication, TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return CategoryCreateSerializer
        # Allow simple public format via ?format=simple for list/retrieve
        try:
            request = getattr(self, 'request', None)
            if request and request.query_params.get('format') == 'simple' and self.action in ['list', 'retrieve']:
                from .serializers import CategorySimpleSerializer
                return CategorySimpleSerializer
        except Exception:
            pass
        return CategorySerializer
    
    def get_permissions(self):
        """Allow public access for read operations"""
        if self.action in ['list', 'retrieve', 'tree', 'products']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        """Get categories with optimized queries"""
        queryset = Category.objects.prefetch_related('children', 'products')
        
        # Filter by parent if specified
        parent_id = self.request.query_params.get('parent')
        if parent_id:
            if parent_id == 'null':
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent_id)
        
        # Filter by name if specified
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        
        return queryset.order_by('name')
    
    @action(detail=False, methods=['GET'])
    def tree(self, request):
        """Get hierarchical category tree"""
        def build_tree(categories, parent=None):
            tree = []
            for category in categories:
                if category.parent == parent:
                    node = {
                        'id': category.id,
                        'name': category.name,
                        'slug': category.slug,
                        'children_count': category.children.count(),
                        'products_count': category.products.count(),
                        'children': build_tree(categories, category)
                    }
                    tree.append(node)
            return tree
        
        # Get all categories
        categories = Category.objects.all()
        tree = build_tree(categories)
        
        return Response({
            'status': 'success',
            'data': tree
        })
    
    @action(detail=True, methods=['GET'])
    def products(self, request, pk=None):
        """Get all products in a specific category"""
        category = self.get_object()
        products = category.products.filter(status='published')
        
        # Pagination
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response({
            'status': 'success',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['POST'])
    def bulk_create(self, request):
        """Create multiple categories at once"""
        categories_data = request.data.get('categories', [])
        
        if not categories_data:
            return Response({
                'status': 'error',
                'message': 'No categories data provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        created_categories = []
        errors = []
        
        for cat_data in categories_data:
            try:
                serializer = self.get_serializer(data=cat_data)
                if serializer.is_valid():
                    category = serializer.save()
                    created_categories.append(category)
                else:
                    errors.append({
                        'data': cat_data,
                        'errors': serializer.errors
                    })
            except Exception as e:
                errors.append({
                    'data': cat_data,
                    'error': str(e)
                })
        
        return Response({
            'status': 'success',
            'message': f'Successfully created {len(created_categories)} categories',
            'created_count': len(created_categories),
            'errors': errors
        })
    
    @action(detail=True, methods=['POST'])
    def move_products(self, request, pk=None):
        """Move all products from one category to another"""
        category = self.get_object()
        target_category_id = request.data.get('target_category_id')
        
        if not target_category_id:
            return Response({
                'status': 'error',
                'message': 'Target category ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_category = Category.objects.get(id=target_category_id)
            products_count = category.products.count()
            
            # Move all products to target category
            category.products.update(category=target_category)
            
            return Response({
                'status': 'success',
                'message': f'Successfully moved {products_count} products from {category.name} to {target_category.name}',
                'moved_count': products_count
            })
        except Category.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Target category not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def perform_create(self, serializer):
        """Custom create method with validation"""
        # Check if slug already exists
        slug = serializer.validated_data.get('slug')
        if Category.objects.filter(slug=slug).exists():
            raise serializers.ValidationError(f"Category with slug '{slug}' already exists")
        
        serializer.save()
    
    def perform_update(self, serializer):
        """Custom update method with validation"""
        instance = serializer.instance
        new_slug = serializer.validated_data.get('slug')
        
        # Check if slug already exists (excluding current instance)
        if Category.objects.filter(slug=new_slug).exclude(id=instance.id).exists():
            raise serializers.ValidationError(f"Category with slug '{new_slug}' already exists")
        
        serializer.save()
            
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

class CustomerListView(generics.ListAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer  # Simple serializer needed
    permission_classes = [IsAdminUser]

# Updated CustomerViewSet with fixes

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerDetailSerializer
    pagination_class = CustomerPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CustomerFilterSet
    search_fields = ['name', 'email', 'phone']
    ordering_fields = ['created_at', 'name', 'orders_count', 'balance']
    ordering = ['-created_at']
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        # Get all customers with proper annotations
        queryset = super().get_queryset().select_related('user').annotate(
            orders_count=Count('user__orders', distinct=True),
            balance=Coalesce(Sum('user__orders__total'), Value(0, output_field=DecimalField()), output_field=DecimalField())
        )
        
        # Apply status filter only if explicitly requested
        status = self.request.query_params.get('status')
        if status:
            if status.lower() == 'active':
                # Show customers with active user accounts OR no user account (guest customers)
                queryset = queryset.filter(
                    Q(user__is_active=True) | Q(user__isnull=True)
                )
            elif status.lower() == 'blocked':
                # Show only customers with inactive user accounts
                queryset = queryset.filter(user__is_active=False, user__isnull=False)
        # If no status filter, show ALL customers (this is the key fix!)
        
        return queryset

    def update(self, request, *args, **kwargs):
        """Custom update method for customers"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Perform the update
        customer = serializer.save()
        
        # Return the updated customer details using CustomerDetailSerializer
        detail_serializer = CustomerDetailSerializer(customer)
        
        return Response({
            'status': 'success',
            'success': True,
            'message': 'Customer updated successfully',
            'data': detail_serializer.data
        }, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests for partial updates"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Custom destroy method to ensure proper synchronization with Django Admin"""
        instance = self.get_object()
        
        # Store user info for logging before deletion
        user_info = None
        if instance.user:
            user_info = {
                'id': instance.user.id,
                'email': instance.user.email
            }
        
        try:
            # If this customer has an associated user, delete the user first
            # This will cascade to delete the Profile and any other related records
            if instance.user:
                user = instance.user
                print(f"🗑️ Deleting associated user {user.id} ({user.email}) due to customer deletion")
                # Delete the user (this will cascade to Profile and other related records)
                user.delete()
                # The Customer record will be automatically deleted due to CASCADE
                print(f"✅ Successfully deleted user {user_info['id']} and all related records")
            else:
                # If no user was associated, just delete the customer
                print(f"🗑️ Deleting customer {instance.id} ({instance.email}) - no associated user")
                instance.delete()
                print(f"✅ Successfully deleted customer {instance.id}")
            
            return Response({
                'status': 'success',
                'success': True,
                'message': 'Customer deleted successfully'
            }, status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            print(f"❌ Error during customer deletion: {e}")
            return Response({
                'status': 'error',
                'success': False,
                'message': f'Error deleting customer: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomerCreateSerializer
        elif self.action == 'list':
            return CustomerSerializer
        elif self.action in ['update', 'partial_update']:
            return CustomerUpdateSerializer
        return CustomerDetailSerializer

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

        customers = Customer.objects.filter(id__in=customer_ids)

        if action == 'update_status':
            new_status = request.data.get('status')
            if new_status not in ['active', 'blocked']:
                return Response({
                    'error': 'Invalid status'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update user accounts if they exist
            for customer in customers:
                if customer.user:
                    customer.user.is_active = (new_status == 'active')
                    customer.user.save()

        elif action == 'delete':
            # Also delete associated user accounts if they exist
            for customer in customers:
                if customer.user:
                    customer.user.delete()
            customers.delete()

        return Response({'status': 'success', 'affected': len(customer_ids)})

    @action(detail=False, methods=['GET'])
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="customers-{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Status', 'Orders', 'Total Balance', 'Created'])
        
        for customer in queryset:
            status_display = 'Active'
            if customer.user:
                status_display = 'Active' if customer.user.is_active else 'Blocked'
            
            writer.writerow([
                customer.id,
                customer.name,
                customer.email,
                customer.phone,
                status_display,
                customer.orders_count,
                f"${customer.balance:,.2f}",
                customer.created_at.strftime('%Y-%m-%d')
            ])
        
        return response

    @action(detail=False, methods=['GET'])
    def debug_info(self, request):
        """Debug endpoint to check customer counts and relationships"""
        from django.db.models import Count
        
        # Get raw counts
        total_customers = Customer.objects.count()
        total_users = CustomUser.objects.count()
        
        # Check customer-user relationships
        customers_with_users = Customer.objects.filter(user__isnull=False).count()
        customers_without_users = Customer.objects.filter(user__isnull=True).count()
        
        # Check user-customer relationships
        users_with_customers = CustomUser.objects.filter(customer__isnull=True).count()
        users_without_customers = CustomUser.objects.filter(customer__isnull=False).count()
        
        # Check active/inactive status
        active_customers = Customer.objects.filter(user__is_active=True).count()
        blocked_customers = Customer.objects.filter(user__is_active=False).count()
        
        # Get sample data
        sample_customers = Customer.objects.all()[:5]
        sample_users = CustomUser.objects.all()[:5]
        
        debug_data = {
            'counts': {
                'total_customers': total_customers,
                'total_users': total_users,
                'customers_with_users': customers_with_users,
                'customers_without_users': customers_without_users,
                'users_with_customers': users_with_customers,
                'users_without_customers': users_without_customers,
                'active_customers': active_customers,
                'blocked_customers': blocked_customers,
            },
            'sample_customers': [
                {
                    'id': c.id,
                    'name': c.name,
                    'email': c.email,
                    'has_user': c.user is not None,
                    'user_active': c.user.is_active if c.user else None,
                } for c in sample_customers
            ],
            'sample_users': [
                {
                    'id': u.id,
                    'email': u.email,
                    'first_name': u.first_name,
                    'last_name': u.last_name,
                    'is_active': u.is_active,
                    'has_customer': hasattr(u, 'customer'),
                } for u in sample_users
            ]
        }
        
        return Response(debug_data)

    @action(detail=True, methods=['POST'])
    def test_update(self, request, pk=None):
        """Test endpoint to verify customer update functionality"""
        try:
            customer = self.get_object()
            
            # Log the current state
            current_data = {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone,
                'status': customer.status,
                'user_active': customer.user.is_active if customer.user else None,
            }
            
            # Test update with provided data
            test_data = request.data.copy()
            serializer = CustomerUpdateSerializer(customer, data=test_data, partial=True)
            
            if not serializer.is_valid():
                return Response({
                    'status': 'error',
                    'success': False,
                    'message': 'Validation error',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Perform update
            updated_customer = serializer.save()
            
            # Get updated data
            updated_data = {
                'id': updated_customer.id,
                'name': updated_customer.name,
                'email': updated_customer.email,
                'phone': updated_customer.phone,
                'status': updated_customer.status,
                'user_active': updated_customer.user.is_active if updated_customer.user else None,
            }
            
            return Response({
                'status': 'success',
                'success': True,
                'message': 'Test update completed',
                'before': current_data,
                'after': updated_data,
                'changes': test_data
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'success': False,
                'message': f'Update failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['GET'])
    def sync_status(self, request, pk=None):
        """Debug endpoint to check sync status between CustomUser, Profile, and Customer"""
        try:
            customer = self.get_object()
            user = customer.user if customer.user else None
            profile = Profile.objects.filter(user=user).first() if user else None
            
            sync_data = {
                'customer': {
                    'id': customer.id,
                    'name': customer.name,
                    'email': customer.email,
                    'phone': customer.phone,
                    'status': customer.status,
                    'user_linked': customer.user is not None,
                },
                'user': {
                    'id': user.id if user else None,
                    'email': user.email if user else None,
                    'first_name': user.first_name if user else None,
                    'last_name': user.last_name if user else None,
                    'is_active': user.is_active if user else None,
                } if user else None,
                'profile': {
                    'id': profile.id if profile else None,
                    'full_name': profile.full_name if profile else None,
                    'phone_number': profile.phone_number if profile else None,
                } if profile else None,
                'sync_issues': []
            }
            
            # Check for sync issues
            if user and profile:
                if customer.name != profile.full_name:
                    sync_data['sync_issues'].append(f"Name mismatch: Customer='{customer.name}' vs Profile='{profile.full_name}'")
                if customer.phone != profile.phone_number:
                    sync_data['sync_issues'].append(f"Phone mismatch: Customer='{customer.phone}' vs Profile='{profile.phone_number}'")
                if customer.email != user.email:
                    sync_data['sync_issues'].append(f"Email mismatch: Customer='{customer.email}' vs User='{user.email}'")
                if customer.status == 'active' and not user.is_active:
                    sync_data['sync_issues'].append(f"Status mismatch: Customer='{customer.status}' vs User.is_active={user.is_active}")
                elif customer.status == 'blocked' and user.is_active:
                    sync_data['sync_issues'].append(f"Status mismatch: Customer='{customer.status}' vs User.is_active={user.is_active}")
            
            return Response({
                'status': 'success',
                'success': True,
                'data': sync_data
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'success': False,
                'message': f'Sync status check failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['GET'])
    def statistics(self, request, pk=None):
        customer = self.get_object()
        orders = Order.objects.filter(customer=customer)
        
        total_orders = orders.count()
        total_spent = orders.aggregate(total=Sum('total'))['total'] or 0
        recent_orders = orders.order_by('-created_at')[:5]
        
        # Additional statistics
        monthly_orders = orders.filter(
            created_at__gte=timezone.now().replace(day=1)
        ).count()
        
        avg_order_value = total_spent / total_orders if total_orders > 0 else 0

        # Abandoned cart count for this customer
        abandoned_carts_count = 0
        if customer.user:  # Check if the customer is linked to a user
            # Use a setting for threshold, default to 24 hours
            abandoned_cart_threshold_hours = getattr(settings, 'ABANDONED_CART_THRESHOLD_HOURS', 24)
            abandoned_threshold_time = timezone.now() - timedelta(hours=abandoned_cart_threshold_hours)
            
            abandoned_carts_count = Cart.objects.filter(
                user=customer.user,
                updated_at__lt=abandoned_threshold_time,
                items__isnull=False  # Ensures the cart has items and is not empty
            ).distinct().count()

        # Order status counts
        order_status_counts = {
            'pending': orders.filter(status='PENDING').count(),
            'processing': orders.filter(status='PROCESSING').count(), # Added for completeness, UI might not show it
            'shipped': orders.filter(status='SHIPPED').count(),       # Added for completeness, UI might not show it
            'completed': orders.filter(status='DELIVERED').count(), # 'DELIVERED' maps to 'Completed' in UI
            'cancelled': orders.filter(status='CANCELLED').count(),
            'returned': orders.filter(status='RETURNED').count(),
            'damaged': orders.filter(status='DAMAGED').count(),
        }
        
        return Response({
            'total_orders': total_orders,
            'total_spent': total_spent,
            'monthly_orders': monthly_orders,
            'avg_order_value': avg_order_value,
            'abandoned_carts_count': abandoned_carts_count,
            'order_status_counts': order_status_counts,
            'recent_orders': OrderSerializer(recent_orders, many=True).data
        })

    @action(detail=False, methods=['POST'])
    def add_customer(self, request):
        serializer = CustomerCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def tracking_history(self, request, pk=None):
        """Return tracking history for the order."""
        order = self.get_object()
        serializer = OrderTrackingSerializer(order.tracking_history.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def dashboard_details(self, request, pk=None):
        """Get detailed customer information for dashboard display"""
        try:
            customer = self.get_object()
            serializer = self.get_serializer(customer)
            return Response({
                'is_success': True,
                'data': serializer.data
            })
        except Customer.DoesNotExist:
            return Response({
                'is_success': False,
                'error': 'Customer not found'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['GET'])
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="customers-{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Status', 'Orders', 'Total Balance', 'Created'])
        
        for customer in queryset:
            status_display = 'Active'
            if customer.user:
                status_display = 'Active' if customer.user.is_active else 'Blocked'
            
            writer.writerow([
                customer.id,
                customer.name,
                customer.email,
                customer.phone,
                status_display,
                customer.orders_count,
                f"${customer.balance:,.2f}",
                customer.created_at.strftime('%Y-%m-%d')
            ])
        
        return response

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for admin notifications"""
    serializer_class = OrderNotificationSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """Get notifications, optionally filtered by read status"""
        queryset = OrderNotification.objects.all()
        
        # Filter by read status if provided
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            is_read = is_read.lower() == 'true'
            queryset = queryset.filter(is_read=is_read)
        
        return queryset
    
    @action(detail=True, methods=['POST'])
    def mark_as_read(self, request, pk=None):
        """Mark a notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        
        return Response({
            'status': 'success',
            'message': 'Notification marked as read'
        })
    
    @action(detail=False, methods=['POST'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read"""
        OrderNotification.objects.filter(is_read=False).update(is_read=True)
        
        return Response({
            'status': 'success',
            'message': 'All notifications marked as read'
        })
    
    @action(detail=False, methods=['GET'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = OrderNotification.objects.filter(is_read=False).count()
        
        return Response({
            'unread_count': count
        })

class ProductVariationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product variations with full CRUD operations
    Supports both single and multiple size/color variations
    """
    queryset = ProductVariation.objects.select_related('product', 'size', 'color').prefetch_related('sizes', 'colors')
    serializer_class = ProductVariationManagementSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'variation_type', 'is_default', 'stock_quantity']
    search_fields = ['sku', 'variation', 'product__name']
    ordering_fields = ['created_at', 'updated_at', 'price_adjustment', 'stock_quantity']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action in ['list', 'retrieve']:
            return ProductVariationManagementSerializer
        return ProductVariationManagementSerializer

    def get_queryset(self):
        """Enhanced queryset with annotations"""
        queryset = super().get_queryset()
        
        # Add annotations for better performance
        queryset = queryset.annotate(
            total_stock=models.F('stock_quantity') + models.Coalesce('product__stock_quantity', 0),
            final_price=models.F('price_adjustment') + models.Coalesce('product__price', 0)
        )
        
        # Filter by product if specified
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Filter by stock status
        stock_status = self.request.query_params.get('stock_status')
        if stock_status:
            if stock_status == 'in_stock':
                queryset = queryset.filter(stock_quantity__gt=0)
            elif stock_status == 'out_of_stock':
                queryset = queryset.filter(stock_quantity=0)
            elif stock_status == 'low_stock':
                queryset = queryset.filter(stock_quantity__gt=0, stock_quantity__lte=10)
        
        return queryset

    def perform_create(self, serializer):
        """Custom create logic with SKU generation"""
        variation = serializer.save()
        
        # Auto-generate SKU if not provided
        if not variation.sku:
            variation.sku = variation.generate_sku()
            variation.save()
        
        # Sync product variations
        if variation.product:
            self.sync_product_variations(variation.product)
        
        return variation

    def perform_update(self, serializer):
        """Custom update logic with sync"""
        variation = serializer.save()
        
        # Sync product variations
        if variation.product:
            self.sync_product_variations(variation.product)
        
        return variation

    def perform_destroy(self, instance):
        """Custom delete logic with sync"""
        product = instance.product
        instance.delete()
        
        # Sync product variations after deletion
        if product:
            self.sync_product_variations(product)

    def sync_product_variations(self, product):
        """Sync product variations to update available sizes and colors"""
        try:
            # Sync available sizes
            product.sync_available_sizes()
            # Sync available colors
            product.sync_available_colors()
        except Exception as e:
            print(f"Error syncing product variations: {e}")

    @action(detail=False, methods=['GET'])
    def by_product(self, request):
        """Get all variations for a specific product"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({'error': 'product_id is required'}, status=400)
        
        variations = self.get_queryset().filter(product_id=product_id)
        serializer = self.get_serializer(variations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def stock_summary(self, request):
        """Get stock summary for all variations"""
        variations = self.get_queryset()
        
        summary = {
            'total_variations': variations.count(),
            'in_stock': variations.filter(stock_quantity__gt=0).count(),
            'out_of_stock': variations.filter(stock_quantity=0).count(),
            'low_stock': variations.filter(stock_quantity__gt=0, stock_quantity__lte=10).count(),
            'total_stock_value': sum(float(v.stock_quantity or 0) * float(v.get_final_price()) for v in variations)
        }
        
        return Response(summary)

    @action(detail=True, methods=['POST'])
    def update_stock(self, request, pk=None):
        """Quick stock update for a variation"""
        variation = self.get_object()
        new_stock = request.data.get('stock_quantity')
        
        if new_stock is not None:
            variation.stock_quantity = new_stock
            variation.save()
            
            # Sync product variations
            if variation.product:
                self.sync_product_variations(variation.product)
            
            return Response({
                'message': 'Stock updated successfully',
                'new_stock': variation.stock_quantity
            })
        
        return Response({'error': 'stock_quantity is required'}, status=400)

    @action(detail=True, methods=['POST'])
    def toggle_default(self, request, pk=None):
        """Toggle the default status of a variation"""
        variation = self.get_object()
        
        # If this variation is being set as default, unset others
        if not variation.is_default:
            # Unset other default variations for this product
            ProductVariation.objects.filter(
                product=variation.product,
                is_default=True
            ).exclude(id=variation.id).update(is_default=False)
            
            variation.is_default = True
            variation.save()
            message = 'Variation set as default'
        else:
            variation.is_default = False
            variation.save()
            message = 'Variation unset as default'
        
        return Response({'message': message, 'is_default': variation.is_default})

    @action(detail=False, methods=['POST'])
    def bulk_update_stock(self, request):
        """Bulk update stock for multiple variations"""
        updates = request.data.get('updates', [])
        if not updates:
            return Response({'error': 'updates array is required'}, status=400)
        
        updated_count = 0
        errors = []
        
        for update in updates:
            try:
                variation_id = update.get('variation_id')
                new_stock = update.get('stock_quantity')
                
                if variation_id is None or new_stock is None:
                    errors.append(f"Missing variation_id or stock_quantity for update: {update}")
                    continue
                
                variation = ProductVariation.objects.get(id=variation_id)
                variation.stock_quantity = new_stock
                variation.save()
                updated_count += 1
                
            except ProductVariation.DoesNotExist:
                errors.append(f"Variation with id {update.get('variation_id')} not found")
            except Exception as e:
                errors.append(f"Error updating variation {update.get('variation_id')}: {str(e)}")
        
        # Sync all affected products
        affected_products = set()
        for update in updates:
            try:
                variation = ProductVariation.objects.get(id=update.get('variation_id'))
                if variation.product:
                    affected_products.add(variation.product)
            except:
                pass
        
        for product in affected_products:
            self.sync_product_variations(product)
        
        return Response({
            'message': f'Successfully updated {updated_count} variations',
            'updated_count': updated_count,
            'errors': errors if errors else None
        })

    @action(detail=False, methods=['GET'])
    def export_csv(self, request):
        """Export variations to CSV"""
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="product_variations.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Product', 'Product SKU', 'Variation Type', 'Variation',
            'Price Adjustment', 'Stock Quantity', 'SKU', 'Is Default',
            'Sizes', 'Colors', 'Created At'
        ])
        
        variations = self.get_queryset()
        for variation in variations:
            sizes = ', '.join([size.name for size in variation.sizes.all()])
            colors = ', '.join([color.name for color in variation.colors.all()])
            
            writer.writerow([
                variation.id,
                variation.product.name if variation.product else '',
                variation.product.sku if variation.product else '',
                variation.variation_type,
                variation.variation,
                variation.price_adjustment,
                variation.stock_quantity,
                variation.sku,
                'Yes' if variation.is_default else 'No',
                sizes,
                colors,
                variation.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response

    @action(detail=False, methods=['GET'])
    def grouped_by_size(self, request):
        """Get product variations grouped by size for frontend dashboard"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({'error': 'product_id is required'}, status=400)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)
        
        # Get all variations for this product
        variations = ProductVariation.objects.filter(product=product).prefetch_related('sizes', 'colors')
        
        # Group variations by size
        grouped_variations = {}
        
        for variation in variations:
            for size in variation.sizes.all():
                size_name = size.name
                
                if size_name not in grouped_variations:
                    grouped_variations[size_name] = {
                        'size_id': size.id,
                        'colors': [],
                        'price': float(variation.price_adjustment + product.price),
                        'stock_quantity': variation.stock_quantity
                    }
                
                # Add colors for this size
                for color in variation.colors.all():
                    color_data = {
                        'id': color.id,
                        'name': color.name,
                        'hex_code': color.hex_code
                    }
                    if color_data not in grouped_variations[size_name]['colors']:
                        grouped_variations[size_name]['colors'].append(color_data)
        
        # Convert to the expected format
        result = {
            'product_id': product.id,
            'product_name': product.name,
            'product_sku': product.sku,
            'variations': grouped_variations
        }
        
        return Response(result)

    @action(detail=False, methods=['POST'])
    def add_size_variant(self, request):
        """Add a new size variant with colors and price for a product"""
        product_id = request.data.get('product_id')
        size_name = request.data.get('size')
        colors = request.data.get('colors', [])
        price = request.data.get('price')
        stock_quantity = request.data.get('stock_quantity', 0)
        
        if not all([product_id, size_name, colors, price]):
            return Response({
                'error': 'product_id, size, colors, and price are required'
            }, status=400)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)
        
        # Get or create the size
        size, created = Size.objects.get_or_create(name=size_name)
        
        # Get or create colors
        color_objects = []
        for color_name in colors:
            color, created = Color.objects.get_or_create(name=color_name)
            color_objects.append(color)
        
        # Calculate price adjustment (price - product base price)
        price_adjustment = float(price) - float(product.price)
        
        # Create variation for this size
        variation = ProductVariation.objects.create(
            product=product,
            variation_type='size',
            variation=size_name,
            price_adjustment=price_adjustment,
            stock_quantity=stock_quantity,
            is_default=False
        )
        
        # Add size and colors
        variation.sizes.add(size)
        variation.colors.set(color_objects)
        
        # Generate SKU
        variation.sku = variation.generate_sku()
        variation.save()
        
        # Return the grouped structure
        return Response({
            'message': f'Size variant "{size_name}" added successfully',
            'variation_id': variation.id,
            'size': size_name,
            'colors': colors,
            'price': price,
            'stock_quantity': stock_quantity
        }, status=201)

    @action(detail=False, methods=['PUT'])
    def update_size_variant(self, request):
        """Update an existing size variant's colors, price, and stock"""
        product_id = request.data.get('product_id')
        size_name = request.data.get('size')
        colors = request.data.get('colors', [])
        price = request.data.get('price')
        stock_quantity = request.data.get('stock_quantity')
        
        if not all([product_id, size_name, colors, price]):
            return Response({
                'error': 'product_id, size, colors, and price are required'
            }, status=400)
        
        try:
            product = Product.objects.get(id=product_id)
            size = Size.objects.get(name=size_name)
        except (Product.DoesNotExist, Size.DoesNotExist):
            return Response({'error': 'Product or size not found'}, status=404)
        
        # Find existing variation for this size
        try:
            variation = ProductVariation.objects.get(
                product=product,
                sizes=size
            )
        except ProductVariation.DoesNotExist:
            return Response({'error': f'No variation found for size "{size_name}"'}, status=404)
        
        # Update price adjustment
        price_adjustment = float(price) - float(product.price)
        variation.price_adjustment = price_adjustment
        
        # Update stock quantity if provided
        if stock_quantity is not None:
            variation.stock_quantity = stock_quantity
        
        # Update colors
        color_objects = []
        for color_name in colors:
            color, created = Color.objects.get_or_create(name=color_name)
            color_objects.append(color)
        
        variation.colors.set(color_objects)
        variation.save()
        
        return Response({
            'message': f'Size variant "{size_name}" updated successfully',
            'size': size_name,
            'colors': colors,
            'price': price,
            'stock_quantity': variation.stock_quantity
        })

    @action(detail=False, methods=['DELETE'])
    def remove_size_variant(self, request):
        """Remove an entire size variant from a product"""
        product_id = request.data.get('product_id')
        size_name = request.data.get('size')
        
        if not all([product_id, size_name]):
            return Response({
                'error': 'product_id and size are required'
            }, status=400)
        
        try:
            product = Product.objects.get(id=product_id)
            size = Size.objects.get(name=size_name)
        except (Product.DoesNotExist, Size.DoesNotExist):
            return Response({'error': 'Product or size not found'}, status=404)
        
        # Find and delete variation for this size
        try:
            variation = ProductVariation.objects.get(
                product=product,
                sizes=size
            )
            variation.delete()
        except ProductVariation.DoesNotExist:
            return Response({'error': f'No variation found for size "{size_name}"'}, status=404)
        
        return Response({
            'message': f'Size variant "{size_name}" removed successfully'
        })