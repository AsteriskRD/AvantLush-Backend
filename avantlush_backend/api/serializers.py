from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.serializers import SocialLoginSerializer, RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
from .models import (
    CustomUser,  
    WaitlistEntry, 
    Product, 
    Article, 
    Cart, 
    CartItem, 
    Order, 
    OrderItem
)

User = get_user_model()

class WaitlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitlistEntry
        fields = ['email']
    
    def validate_email(self, value):
        # Optional: Add any additional email validation if needed
        if WaitlistEntry.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already on the waitlist.')
        return value
    
class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})
    location = serializers.CharField(required=True)
    agreed_to_terms = serializers.BooleanField(required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'password_confirm', 'location', 'agreed_to_terms')

    def validate(self, data):
        # Existing password validation
        password = data.get('password')
        password_confirm = data.pop('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })

        try:
            validate_password(password)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({
                'password': list(e.messages)
            })

        # Terms validation
        if not data.get('agreed_to_terms'):
            raise serializers.ValidationError({
                'agreed_to_terms': 'You must accept the terms and privacy policy.'
            })

        # Location validation
        if not data.get('location'):
            raise serializers.ValidationError({
                'location': 'Location is required.'
            })

        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    def validate(self, data):
        """
        Custom validation to check if user exists and password is correct
        Note: Actual authentication happens in the view
        """
        email = data.get('email')
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                'email': 'No account found with this email address.'
            })
        return data

User = get_user_model()

class GoogleAuthSerializer(SocialLoginSerializer):
    token = serializers.CharField(required=True)
    username = None  # Remove username field

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Google token is required")
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if 'user' in attrs and not attrs['user'].email:
            raise serializers.ValidationError('Email is required')
        return attrs

    def get_social_login(self, adapter, app, token, response):
        request = self.context.get('request')
        social_login = adapter.complete_login(request, app, token, response=response)
        social_login.token = token
        return social_login

class CustomUserDetailsSerializer(UserDetailsSerializer):
    class Meta(UserDetailsSerializer.Meta):
        fields = ('email', 'first_name', 'last_name')
        read_only_fields = ('email',)

class CustomRegisterSerializer(RegisterSerializer):
    username = None  # Remove username field
    
    def get_cleaned_data(self):
        return {
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', '')
        }

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at', 'updated_at']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
