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
from django.template.loader import render_to_string
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
@throttle_classes([WaitlistRateThrottle])
def waitlist_signup(request):
    try:
        serializer = WaitlistSerializer(data=request.data)
        if serializer.is_valid():
            waitlist_entry = serializer.save()

            #import os
            #print("Template path:", os.path.join(settings.BASE_DIR, 'api', 'templates', 'waitlist_email.html'))

            # Send confirmation email
            html_message = render_to_string('waitlist-email(1).html')
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

@api_view(['POST'])
def register(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
