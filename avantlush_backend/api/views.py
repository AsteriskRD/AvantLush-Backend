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
from .models import Product, Article, Cart, CartItem, Order, WaitlistEntry
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from .serializers import GoogleAuthSerializer

class WaitlistRateThrottle(AnonRateThrottle):
    rate = '5/minute'  # Limit to 5 requests per minute per IP

class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH2_CALLBACK_URL  # You'll need to add this to settings.py
    client_class = OAuth2Client
    serializer_class = GoogleAuthSerializer
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
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                'success': True,
                'token': token.key,
                'email': user.email,
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
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
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

class OrderViewSet(viewsets.GenericViewSet,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   mixins.UpdateModelMixin):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        try:
            order = self.get_queryset().get(pk=pk)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(order, data={'status': request.data.get('status')}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
