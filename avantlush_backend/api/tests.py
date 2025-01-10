from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import WaitlistEntry
import json

class WaitlistTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_email = "test@example.com"
        self.invalid_email = "invalid-email"
        
    def test_valid_signup(self):
        response = self.client.post('/api/waitlist/signup/', 
                                  {'email': self.valid_email}, 
                                  format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(WaitlistEntry.objects.filter(email=self.valid_email).exists())
    
    def test_invalid_email(self):
        response = self.client.post('/api/waitlist/signup/', 
                                  {'email': self.invalid_email}, 
                                  format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_duplicate_email(self):
        # First signup
        self.client.post('/api/waitlist/signup/', 
                        {'email': self.valid_email}, 
                        format='json')
        # Duplicate signup
        response = self.client.post('/api/waitlist/signup/', 
                                  {'email': self.valid_email}, 
                                  format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_rate_limiting(self):
        # Test rate limiting by making multiple requests
        for _ in range(6):  # Exceed the rate limit (5/minute)
            self.client.post('/api/waitlist/signup/', 
                           {'email': f"test{_}@example.com"}, 
                           format='json')
        response = self.client.post('/api/waitlist/signup/', 
                                  {'email': 'another@example.com'}, 
                                  format='json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        
    def test_api_documentation(self):
        """Test API documentation endpoints"""
        response = self.client.get('/swagger/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get('/redoc/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = self.client.options('/api/waitlist/signup/', 
            HTTP_ORIGIN='http://localhost:3000')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.has_header('Access-Control-Allow-Origin'))        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)