from django.utils.deprecation import MiddlewareMixin
import json
from django.http import JsonResponse

class StandardizedResponseMiddleware(MiddlewareMixin):
    """
    Middleware to standardize API responses with an is_success field
    """
    def process_response(self, request, response):
        # Only process API responses
        if not request.path.startswith('/api/'):
            return response
            
        # Skip non-JSON responses
        if not hasattr(response, 'content') or not response.get('Content-Type', '').startswith('application/json'):
            return response
            
        # Parse the response content
        try:
            content = json.loads(response.content.decode('utf-8'))
            
            # Skip if already has is_success field
            if 'is_success' in content:
                return response
                
            # Add is_success field based on HTTP status code
            is_success = 200 <= response.status_code < 300
            
            # Create new response structure
            new_content = {
                'is_success': is_success,
                'data': content
            }
            
            # If error, add message field
            if not is_success and isinstance(content, dict) and 'detail' in content:
                new_content['message'] = content['detail']
                
            # Return new response
            return JsonResponse(new_content, status=response.status_code)
            
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Not a valid JSON response, return unchanged
            return response
