from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.serializers import SocialLoginSerializer, RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from rest_framework import serializers
import re
from rest_framework import serializers
from .models import Profile, Address
from .utils import VALID_COUNTRY_CODES, validate_phone_format, format_phone_number
from .models import Wishlist, WishlistItem, ProductRecommendation
from .models import (
    CustomUser,  
    WaitlistEntry, 
    Product,
    Category, 
    Article, 
    Cart, 
    CartItem, 
    Order, 
    OrderItem,
    Profile,  
    Address
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
    location = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'location', 'uuid')
        read_only_fields = ('uuid',)


    def validate_email(self, value):
        # Log the email being validated
        print(f"Validating email: {value}")
        
        # Check if user exists
        exists = CustomUser.objects.filter(email__iexact=value).exists()
        print(f"User exists: {exists}")
        
        if exists:
            raise serializers.ValidationError("User with this email address already exists.")
        return value

    def validate(self, data):
        password = data.get('password')

        try:
            validate_password(password)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({
                'password': list(e.messages)
            })

        return data

    def create(self, validated_data):
        print(f"Creating user with data: {validated_data}")
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
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    
    def validate_password(self, value):
        try:
            validate_password(value)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

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

class AppleAuthSerializer(SocialLoginSerializer):
    token = serializers.CharField(required=True)
    code = serializers.CharField(required=False)  # Apple specific
    id_token = serializers.CharField(required=False)  # Apple specific

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Apple token is required")
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

class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    photo_url = serializers.SerializerMethodField()
    country_code = serializers.CharField(max_length=4, required=True)
    formatted_phone_number = serializers.SerializerMethodField()
    available_country_codes = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = [
            'id', 'email', 'full_name', 'phone_number', 
            'country_code', 'formatted_phone_number', 
            'photo', 'photo_url', 'updated_at',
            'available_country_codes'
        ]
        read_only_fields = ['id', 'email', 'updated_at', 'formatted_phone_number', 'available_country_codes']
    
    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None
    
    def get_formatted_phone_number(self, obj):
        if obj.phone_number and hasattr(obj, 'country_code'):
            return format_phone_number(obj.country_code, obj.phone_number)
        return None
    
    def get_available_country_codes(self, obj):
        return {code: name for code, name in VALID_COUNTRY_CODES.items()}
    
    def validate(self, data):
        country_code = data.get('country_code')
        phone_number = data.get('phone_number')
        
        if country_code and phone_number:
            is_valid, error_message = validate_phone_format(country_code, phone_number)
            if not is_valid:
                raise serializers.ValidationError({'phone_number': error_message})
            
            # Format the phone number before saving
            data['phone_number'] = format_phone_number(country_code, phone_number)
        
        return data
    
    def validate_country_code(self, value):
        if not value.startswith('+'):
            raise serializers.ValidationError("Country code must start with '+'")
        
        if value not in VALID_COUNTRY_CODES:
            raise serializers.ValidationError(
                f"Invalid country code. Valid options are: {', '.join(VALID_COUNTRY_CODES.keys())}"
            )
        return value
    
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street_address', 'city', 'state', 'country',
                 'zip_code', 'is_default', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_zip_code(self, value):
        if not re.match(r'^\d{5}(-\d{4})?$', value):
            raise serializers.ValidationError("Invalid zip code format")
        return value
    
    def validate_street_address(self, value):
        if not value.strip():
            raise serializers.ValidationError("Street address cannot be empty")
        return value
    
    def validate_city(self, value):
        if not value.strip():
            raise serializers.ValidationError("City cannot be empty")
        return value
    
    def validate_state(self, value):
        if not value.strip():
            raise serializers.ValidationError("State cannot be empty")
        return value
    
    def validate_country(self, value):
        if not value.strip():
            raise serializers.ValidationError("Country cannot be empty")
        return value

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 
            'category', 'category_name', 'images', 'stock_quantity',
            'is_featured', 'sku', 'status', 'created_at', 'updated_at'
        ]
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent']


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

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'products']

class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = ['id', 'wishlist', 'product', 'added_at']

class ProductRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRecommendation
        fields = ['id', 'product', 'recommended_product', 'score']