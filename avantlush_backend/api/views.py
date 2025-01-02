from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import AnonRateThrottle
from .serializers import WaitlistSerializer, RegistrationSerializer, LoginSerializer
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

class WaitlistRateThrottle(AnonRateThrottle):
    rate = '5/minute'  # Limit to 5 requests per minute per IP

@api_view(['GET'])
def api_root(request):
    return Response({
        'status': 'API is running',
        'available_endpoints': {
            'waitlist_signup': '/api/waitlist/signup/',
            'register': '/api/register/',
            'login': '/api/login/',
            'admin': '/admin/',
        }
    })

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import WaitlistEntry

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
                SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
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
@throttle_classes([WaitlistRateThrottle])
def waitlist_signup(request):
    try:
        serializer = WaitlistSerializer(data=request.data)
        if serializer.is_valid():
            waitlist_entry = serializer.save()

            #import os
            #print("Template path:", os.path.join(settings.BASE_DIR, 'api', 'templates', 'waitlist_email.html'))

            # Send confirmation email
            html_message = render_to_string('waitlist-email(1).html', {'email': waitlist_entry.email})
            plain_message = strip_tags(html_message)

            send_mail(
                'Thank You For Joining The Avantlush Wailtlist',
                plain_message,
                'avalusht@gmail.com',
                [waitlist_entry.email],
                html_message=html_message,
                fail_silently=False,
            )

            return Response({
                'message': 'Successfully added to waitlist',
                'email': waitlist_entry.email,
                'status_code': status.HTTP_201_CREATED
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': serializer.errors,
                'status_code': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

    except ValidationError as e:
        return Response({
            'error': str(e),
            'status_code': status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e),
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def preview_email(request):
    return render(request, 'waitlist-email(1).html')

# Update register function:
@api_view(['POST'])
def register(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'email': user.email,
            'location': user.location
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = authenticate(
            request,
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'email': user.email,
                'location': user.location
            }, status=status.HTTP_200_OK)
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
