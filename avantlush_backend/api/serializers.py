from rest_framework import serializers
from .models import WaitlistEntry
import re

class WaitlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitlistEntry
        fields = ['email', 'created_at']
        read_only_fields = ['created_at']
    
    def validate_email(self, value):
        # Check for existing email
        if WaitlistEntry.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already on the waitlist.")
        
        # Additional email validation
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(value):
            raise serializers.ValidationError("Please enter a valid email address.")
            
        return value.lower()  # Store emails in lowercase