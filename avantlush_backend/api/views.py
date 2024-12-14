from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import AnonRateThrottle
from .serializers import WaitlistSerializer
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

class WaitlistRateThrottle(AnonRateThrottle):
    rate = '5/minute'  # Limit to 5 requests per minute per IP

@api_view(['GET'])
def api_root(request):
    return Response({
        'status': 'API is running',
        'available_endpoints': {
            'waitlist_signup': '/api/waitlist/signup/',
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
            
            # Send confirmation email
            send_mail(
                'Welcome to Avantlush Waitlist',
                'Thank you for joining our waitlist. We will keep you updated on our launch!',
                'noreply@avantlush.com',
                [waitlist_entry.email],
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
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def your_api_view(request):
    try:
        # Your existing view logic
        return Response({
            'data': your_data,
            'status_code': status.HTTP_200_OK
        })
    except Exception as e:
        logger.error(f"Detailed error: {str(e)}")
        return Response({
            'error': str(e),
            'detail': f"Detailed error: {str(e)}",
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)       