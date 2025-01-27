from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import AnonRateThrottle
from .serializers import WaitlistSerializer, RegistrationSerializer, LoginSerializer, ProductSerializer, ArticleSerializer, CartSerializer, CartItemSerializer, OrderSerializer, GoogleAuthSerializer
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import rest_framework
from django.template.loader import render_to_string
from google.oauth2 import id_token
from google.auth.transport import requests
from django.utils.html import strip_tags
from django.shortcuts import render
from .models import Product, Article, Cart, CartItem, Order, WaitlistEntry, CustomUser, PasswordResetToken
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from .serializers import GoogleAuthSerializer
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from .models import EmailVerificationToken
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.core.exceptions import ObjectDoesNotExist
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from .serializers import GoogleAuthSerializer, AppleAuthSerializer 
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from .models import CustomUser
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .serializers import ProfileSerializer
from .serializers import AddressSerializer
from .models import Profile
from rest_framework.response import Response
from .models import Profile, Address
from .serializers import ProfileSerializer, AddressSerializer
from .models import Wishlist, WishlistItem, ProductRecommendation
from .serializers import WishlistSerializer, WishlistItemSerializer, ProductRecommendationSerializer
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters import rest_framework as django_filters
from django.db.models import Count
from .models import Review, ReviewTag, ReviewHelpfulVote
from .serializers import ReviewSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .models import Cart, CartItem, Product
from .serializers import CartItemSerializer

from .serializers import (
    WaitlistSerializer, 
    RegistrationSerializer, 
    LoginSerializer,
    
    ForgotPasswordSerializer,
    ResetPasswordSerializer
)
import uuid

class WaitlistRateThrottle(AnonRateThrottle):
    rate = '5/minute'  # Limit to 5 requests per minute per IP

class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH2_CALLBACK_URL  # You'll need to add this to settings.py
    client_class = OAuth2Client
    serializer_class = GoogleAuthSerializer

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
def google_auth(request):
    serializer = GoogleAuthSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['token']
        email = serializer.validated_data['email']
        location = serializer.validated_data.get('location', 'Nigeria')

        try:
            # Verify the Google token
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY  # Use settings for global constants
            )

            if idinfo['email'] != email:
                return Response(
                    {'error': 'Email verification failed'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get or create user
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User.objects.create_user(
                    email=email,
                    location=location,
                    google_id=idinfo['sub']
                )

            # Create or get token
            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'email': user.email,
                'location': user.location
            })

        except ValueError:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth_callback(request):
    """
    Handle Google OAuth callback
    """
    serializer = GoogleAuthSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'user_id': user.id,
            'email': user.email,
            'message': 'Successfully authenticated with Google'
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            
            # Create verification URL - Update the order of parameters
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{verification_token.token}/{urlsafe_base64_encode(force_bytes(user.pk))}"
            
            # Prepare email context
            context = {
                'verification_url': verification_url,
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
        
        # Create verification URL
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{urlsafe_base64_encode(force_bytes(user.pk))}/{verification_token.token}"
        
        # Prepare email context
        context = {
            'verification_url': verification_url,
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

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['price', 'created_at', 'name']
    filterset_fields = ['category', 'status', 'is_featured']
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

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
            
            # Create reset URL
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{urlsafe_base64_encode(force_bytes(user.pk))}/{reset_token.token}"
            
            # Prepare email context
            context = {
                'reset_url': reset_url,
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
    
class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return Response({
                'status': 'success',
                'message': 'Profile updated successfully',
                'data': response.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['POST'])
    def upload_photo(self, request):
        try:
            profile = request.user.profile
            photo = request.FILES.get('photo')
            if not photo:
                return Response({
                    'status': 'error',
                    'message': 'No photo provided'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            profile.photo = photo
            profile.save()
            
            return Response({
                'status': 'success',
                'message': 'Photo uploaded successfully',
                'data': ProfileSerializer(profile, context={'request': request}).data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
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
                'message': 'Photo removed successfully'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response({
                'status': 'success',
                'message': 'Address added successfully',
                'data': response.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return Response({
                'status': 'success',
                'message': 'Address updated successfully',
                'data': response.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['POST'])
    def set_default(self, request, pk=None):
        try:
            address = self.get_object()
            address.is_default = True
            address.save()
            return Response({
                'status': 'success',
                'message': 'Address set as default successfully'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['add_item', 'update_quantity']:
            return CartItemSerializer
        return CartSerializer

    def get_cart(self):
        """Get or create cart for current user"""
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

    @action(detail=False, methods=['GET'])
    def summary(self, request):
        """Get cart summary with totals"""
        cart = self.get_cart()
        items = CartItem.objects.filter(cart=cart).select_related('product')
        
        subtotal = sum(item.product.price * item.quantity for item in items)
        shipping = Decimal('0.00')  # Can be calculated based on your logic
        
        return Response({
            'items': CartItemSerializer(items, many=True).data,
            'subtotal': subtotal,
            'shipping': shipping,
            'total': subtotal + shipping,
            'item_count': items.count()
        })

    @action(detail=False, methods=['POST'])
    def add_item(self, request):
        """Add item to cart"""
        cart = self.get_cart()
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id)
            
            # Check if product is in stock
            if product.stock_quantity < quantity:
                return Response(
                    {'error': 'Not enough stock available'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update or create cart item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return Response(CartItemSerializer(cart_item).data)
            
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(cart=self.request.user.cart)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart_item = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = self.perform_create(serializer)

        # cross-sell products to the order
        cart_items = CartItem.objects.filter(cart__user=request.user)
        for cart_item in cart_items:
            recommendations = ProductRecommendation.objects.filter(product=cart_item.product)
            for recommendation in recommendations:
                OrderItem.objects.create(
                    order=order,
                    product=recommendation.recommended_product,
                    quantity=1,
                    price=recommendation.recommended_product.price
                )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = self.get_serializer(order, data={'status': request.data.get('status')}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
# Product Search and Filtering Views
class ProductSearchView(generics.ListAPIView):
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'description', 'sku', 'tags__name', 'categories__name']
    filterset_fields = ['category', 'tags', 'is_featured', 'status']

# Wishlist Views
class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WishlistItemViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WishlistItem.objects.filter(wishlist__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(wishlist=self.request.user.wishlist)

# Product Recommendation View
class ProductRecommendationView(generics.ListAPIView):
    serializer_class = ProductRecommendationSerializer

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductRecommendation.objects.filter(product_id=product_id)

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