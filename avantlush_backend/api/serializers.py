from rest_framework import serializers
from .models import WaitlistEntry
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.password_validation import validate_password
import re

User = get_user_model()
class GoogleAuthSerializer(serializers.Serializer):
    token = serializers.CharField()
    email = serializers.EmailField()
    location = serializers.CharField(required=False, default='Nigeria')
    
class WaitlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitlistEntry
        fields = ['email', 'created_at']
        read_only_fields = ['created_at']

    def validate_email(self, value):
        if WaitlistEntry.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already on the waitlist.")
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(value):
            raise serializers.ValidationError("Please enter a valid email address.")
        return value.lower()

import os

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    location = serializers.CharField(required=False, default=os.getenv('DEFAULT_LOCATION', 'Nigeria'))

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'location')
        extra_kwargs = {
            'email': {'required': True},
            'location': {'required': False, 'default': os.getenv('DEFAULT_LOCATION', 'Nigeria')}
        }

    def create(self, validated_data):
        user = self.Meta.model.objects.create_user(
            email=validated_data['email'],
            location=validated_data.get('location', 'Nigeria'),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
