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
from rest_framework import serializers
from .models import Review, ReviewTag, ReviewHelpfulVote
from .models import PromoCode, ShippingMethod
from rest_framework import serializers
from .models import SupportTicket, TicketResponse
from rest_framework import serializers
from .models import Order, CustomUser, Cart, Product
from rest_framework import serializers
from .models import Product, Category
from django.contrib.auth import authenticate

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
    OrderTracking,
    WishlistNotification,
    Profile,  
    Address,
    TicketResponse,
    SupportTicket,
    Payment,
    ProductVariation, 
    Tag,
    Category,
    models,
    Customer,
    ProductVariantImage,
    CarouselItem,
    Size,
    Color,
    ProductSize,
    ProductColor,

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
        """
        email = data.get('email')
        password = data.get('password')
        
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                'email': 'No account found with this email address.'
            })
        
        # Add authentication and set the user in the data
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError({
                'password': 'Invalid password for this account.'
            })
            
        # This is what dj_rest_auth expects
        data['user'] = user
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

from rest_framework import serializers
from rest_framework import serializers

class GoogleAuthSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    location = serializers.CharField(required=False, default='Nigeria')

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Google token is required")
        return value
    
    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required")
        return value.lower()  # Normalize email to lowercase

    def validate(self, attrs):
        if not attrs.get('location'):
            attrs['location'] = 'Nigeria'
        return attrs

class GoogleAuthCallbackSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    location = serializers.CharField(required=False, default='Nigeria')

    def validate_code(self, value):
        if not value:
            raise serializers.ValidationError("Authorization code is required")
        return value
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
    """
    Custom serializer for the User model that inherits from dj-rest-auth's UserDetailsSerializer
    Extends the default serializer to include custom fields from CustomUser model
    """
    # Add any custom fields from your CustomUser model
    uuid = serializers.UUIDField(read_only=True)
    location = serializers.CharField(required=False, allow_blank=True)
    
    class Meta(UserDetailsSerializer.Meta):
        model = CustomUser
        fields = UserDetailsSerializer.Meta.fields + (
            'uuid',
            'location',
            # Add any other custom fields from your CustomUser model
        )
        read_only_fields = UserDetailsSerializer.Meta.read_only_fields + (
            'uuid',
        )
    
    def update(self, instance, validated_data):
        """
        Override update method to handle custom fields
        """
        # Handle custom fields first
        instance.location = validated_data.get('location', instance.location)
        
        # Let the parent class handle the rest of the fields
        instance = super().update(instance, validated_data)
        
        return instance
class CustomerDetailSerializer(serializers.ModelSerializer):
    orders_count = serializers.SerializerMethodField()
    total_balance = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'created_at', 
                 'orders_count', 'total_balance', 'status']

    def get_orders_count(self, obj):
        return Order.objects.filter(customer=obj).count()

    def get_total_balance(self, obj):
        return Order.objects.filter(customer=obj).aggregate(
            total=Sum('total'))['total'] or 0

    def get_status(self, obj):
        return 'Active' if obj.user.is_active else 'Blocked'

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

class UserDetailsUpdateSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    photo = serializers.ImageField(required=False)
    phone_number = serializers.CharField(required=False)
    country_code = serializers.CharField(required=False)
    
    def validate_email(self, value):
        # Check if email is already taken by another user
        user = self.context.get('request').user
        if CustomUser.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value
    
    def validate(self, data):
        country_code = data.get('country_code')
        phone_number = data.get('phone_number')
        
        if phone_number and not country_code:
            raise serializers.ValidationError({'country_code': 'Country code is required when providing a phone number'})
        
        if country_code and phone_number:
            is_valid, error_message = validate_phone_format(country_code, phone_number)
            if not is_valid:
                raise serializers.ValidationError({'phone_number': error_message})
            
            # Format the phone number before saving
            data['phone_number'] = format_phone_number(country_code, phone_number)
        
        return data
    
    def update(self, instance, validated_data):
        user = instance.user
        
        # Update email (in CustomUser model)
        if 'email' in validated_data:
            user.email = validated_data['email']
            user.save()
        
        # Update full_name (in Profile model)
        if 'full_name' in validated_data:
            instance.full_name = validated_data['full_name']
        
        # Update photo (in Profile model)
        if 'photo' in validated_data:
            # If there's an existing photo, delete it first
            if instance.photo:
                instance.photo.delete()
            instance.photo = validated_data['photo']
        
        # Update phone_number and country_code
        if 'phone_number' in validated_data:
            instance.phone_number = validated_data['phone_number']
        
        if 'country_code' in validated_data:
            instance.country_code = validated_data['country_code']
        
        instance.save()
        return instance
        
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'full_name', 'email', 'phone_number', 'street_address', 
                 'city', 'state', 'country', 'zip_code', 'is_default', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_zip_code(self, value):
        # Basic validation - just to ensure it's not empty and has reasonable length
        if not value.strip():
            raise serializers.ValidationError("Zip/postal code cannot be empty")
        if len(value) > 20:  # Set a reasonable maximum length
            raise serializers.ValidationError("Zip/postal code is too long")
        return value
    
    def validate_email(self, value):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError("Invalid email format")
        return value
    
    def validate_phone_number(self, value):
        if not re.match(r'^\+?[0-9]{10,15}$', value):
            # Simple clear message instead of technical error
            raise serializers.ValidationError("Please enter a valid phone number")
        return value
    
    def validate_full_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Full name cannot be empty")
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
    main_image = serializers.SerializerMethodField()
    is_featured = serializers.BooleanField()  
    is_physical_product = serializers.BooleanField()
    is_liked = serializers.SerializerMethodField()

    def get_main_image(self, obj):
        if obj.main_image:
            return obj.main_image.url
        return None

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return WishlistItem.objects.filter(
                wishlist__user=request.user,
                product_id=obj.id
            ).exists()
        return False
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 
            'category', 'category_name', 'images', 'stock_quantity',
            'is_featured', 'is_physical_product', 'sku', 'status', 
            'created_at', 'updated_at', 'rating', 'num_ratings', 
            'main_image', 'is_liked', 'product_details'  
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
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    stock_status = serializers.CharField(source='product.status', read_only=True)
    product_image = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'product_name', 'product_price', 'stock_status', 'product_image']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['cart_item_id'] = representation.pop('id')
        return representation
    def get_product_image(self, obj):
        # Check if product has a main image
        if obj.product.main_image:
            return obj.product.main_image.url
        
        # If no main image, check if it has any images in the images list
        elif obj.product.images and len(obj.product.images) > 0:
            return obj.product.images[0]  # Return the first image URL
            
        return None  # Return None if no images are available
            
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['cart_id'] = representation.pop('id')
        return representation
    
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'method', 'amount', 'status', 'created_at']
        
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_sku = serializers.CharField(source='product.sku')
    unit_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    
    def get_unit_price(self, obj):
        # Return the price from elsewhere, or a default value
        return getattr(obj, 'price', 0)
    
    def get_total_price(self, obj):
        # Calculate total price on the fly
        unit_price = self.get_unit_price(obj)
        quantity = getattr(obj, 'quantity', 1)
        return unit_price * quantity
    
    def get_variants(self, obj):
        # Return empty dict or default value
        return {}
        
    def get_product_image(self, obj):
        # Get main image URL
        if obj.product.main_image:
            return obj.product.main_image.url
        elif obj.product.images and len(obj.product.images) > 0:
            return obj.product.images[0]
        return None
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_sku', 'quantity',
                 'unit_price', 'total_price', 'variants', 'product_image']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    customer_email = serializers.EmailField(source='user.email', read_only=True)
    customer_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    payment = serializers.SerializerMethodField()
    estimated_delivery_date = serializers.SerializerMethodField()
    
    # Add this method to get the first payment (if any)
    def get_payment(self, obj):
        payment = obj.payments.first()
        if payment:
            return PaymentSerializer(payment).data
        return None
    
    def get_estimated_delivery_date(self, obj):
        # Look for tracking entry with "Estimated Delivery" status
        estimated_delivery = obj.tracking_history.filter(status="Estimated Delivery").first()
        
        if estimated_delivery:
            # Extract date from description using regex
            import re
            match = re.search(r'by ([A-Za-z]+, [A-Za-z]+ \d+, \d{4})', estimated_delivery.description)
            if match:
                return match.group(1)
        
        # If no specific tracking entry, calculate based on order type and date
        if obj.order_type == 'EXPRESS':
            days = 2
        else:  # STANDARD
            days = 5
            
        from django.utils import timezone
        from datetime import timedelta
        
        base_date = obj.created_at
        delivery_date = base_date + timedelta(days=days)
        
        # Format the date nicely
        return delivery_date.strftime("%A, %B %d, %Y")
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer_email', 'customer_name',
            'items', 'total', 'status', 'status_display', 'payment', 'payments',
            'shipping_address', 'created_at', 'estimated_delivery_date',
            'updated_at', 'note', 'payment_type', 'order_type',
            'order_date', 'order_time'
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']
    
    def get_customer_name(self, obj):
        if obj.user.first_name or obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return obj.user.email
    
    def get_status_display(self, obj):
        return obj.get_status_display()


class OrderCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    payment_method = serializers.CharField(write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'items', 'payment_method', 'shipping_address',
            'billing_address', 'note', 'payment_type', 'order_type',
            'order_date', 'order_time', 'status'  # Added fields from OrderDetailSerializer
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        payment_method = validated_data.pop('payment_method')
        
        # Create order
        order = Order.objects.create(
            user=self.context['request'].user,
            **validated_data
        )
        
        # Create order items
        total = 0
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            quantity = item_data['quantity']
            unit_price = product.price
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                total_price=unit_price * quantity,
                variants=item_data.get('variants', {})
            )
            total += unit_price * quantity
        
        # Update order total
        order.total = total
        order.save()
        
        # Create payment
        Payment.objects.create(
            order=order,
            method=payment_method,
            amount=total,
            status='pending'
        )
        
        return order

class OrderTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTracking
        fields = ['id', 'status', 'location', 'description', 'timestamp']
        read_only_fields = ['timestamp']

class WishlistSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'products', 'products_count']
        
    def get_products(self, obj):
        # Get unique products from wishlist items and order them by added_at
        wishlist_items = obj.items.all().select_related('product').order_by('added_at')
        products_data = []
        
        # Track products we've already added
        added_product_ids = set()
        
        for item in wishlist_items:
            product = item.product
            
            # Skip if we've already added this product
            if product.id in added_product_ids:
                continue
                
            added_product_ids.add(product.id)
            
            # Get main image URL
            main_image = None
            if product.main_image:
                main_image = product.main_image.url
            elif product.images and len(product.images) > 0:
                main_image = product.images[0]
            
            # Remove item_id completely and only use product id
            products_data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'main_image': main_image,
                'images': product.images,
                'price': product.price,
                'is_liked': True,  # Always True for wishlist items
                'status': product.status,
                # 'item_id': item.id,  <-- Remove this field completely
                'added_at': item.added_at
            })
        
        return products_data
    
    def get_products_count(self, obj):
        # Get unique product IDs using similar logic as in get_products
        wishlist_items = obj.items.all().select_related('product')
        added_product_ids = set()
        
        for item in wishlist_items:
            added_product_ids.add(item.product.id)
            
        return len(added_product_ids)
    
class WishlistItemSerializer(serializers.ModelSerializer):
    product_details = serializers.SerializerMethodField()
    
    class Meta:
        model = WishlistItem
        fields = ['id', 'wishlist', 'product', 'added_at', 'product_details']
        read_only_fields = ['wishlist']
    
    def get_product_details(self, obj):
        product = obj.product
        
        # Get main image URL
        main_image = None
        if product.main_image:
            main_image = product.main_image.url
        elif product.images and len(product.images) > 0:
            main_image = product.images[0]
            
        return {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'main_image': main_image,
            'images': product.images,
            'price': product.price,
            'status': product.status,
            'is_liked': True
        }
    
    def create(self, validated_data):
        # Get the current user
        user = self.context['request'].user
        # Get or create their wishlist
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        
        # Check if the product is already in the wishlist
        existing_item = WishlistItem.objects.filter(
            wishlist=wishlist, 
            product=validated_data['product']
        ).first()
        
        # If the item already exists, return the existing item
        if existing_item:
            return existing_item
        
        # Add the wishlist to the validated data
        validated_data['wishlist'] = wishlist
        return super().create(validated_data)
    
class WishlistNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistNotification
        fields = ['id', 'notification_type', 'message', 'is_read', 'created_at']
        read_only_fields = ['created_at']


from cloudinary.utils import cloudinary_url

class ProductRecommendationSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'main_image', 'slug', 'rating', 'stock_quantity']
    
    def get_main_image(self, obj):
        if obj.main_image:
            # Get the full URL from Cloudinary
            url, options = cloudinary_url(obj.main_image.public_id, format=obj.main_image.format)
            return url
        return None

class ReviewTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewTag
        fields = ['id', 'name', 'slug', 'count']

class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    tags = ReviewTagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    helpful_count = serializers.IntegerField(source='helpful_votes', read_only=True)
    is_helpful = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'product', 'user_email', 'rating', 'content',
            'images', 'tags', 'tag_ids', 'helpful_count', 'is_helpful',
            'variant', 'is_verified_purchase', 'created_at'
        ]
        read_only_fields = ['user', 'helpful_votes', 'is_verified_purchase']

    def get_is_helpful(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ReviewHelpfulVote.objects.filter(
                review=obj,
                user=request.user
            ).exists()
        return False

    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        review = Review.objects.create(**validated_data)
        if tag_ids:
            review.tags.set(tag_ids)
            # Update tag counts
            ReviewTag.objects.filter(id__in=tag_ids).update(count=models.F('count') + 1)
        return review

class ReviewSummarySerializer(serializers.ModelSerializer):
    """Serializer for aggregated review data shown at the top of reviews"""
    rating_distribution = serializers.SerializerMethodField()
    tag_distribution = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['rating_distribution', 'tag_distribution']

    def get_rating_distribution(self, obj):
        reviews = Review.objects.filter(product=obj.product)
        distribution = {i: reviews.filter(rating=i).count() for i in range(1, 6)}
        return distribution

    def get_tag_distribution(self, obj):
        reviews = Review.objects.filter(product=obj.product)
        tags = ReviewTag.objects.filter(reviews__in=reviews).annotate(
            count=models.Count('reviews')
        ).values('name', 'count')
        return {tag['name']: tag['count'] for tag in tags}
    
class SavedCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'card_brand', 'card_last_four', 'card_expiry']

class ShippingMethodSerializer(serializers.ModelSerializer):
    delivery_date = serializers.SerializerMethodField()

    class Meta:
        model = ShippingMethod
        fields = ['id', 'name', 'price', 'estimated_days', 'description', 'delivery_date']

    def get_delivery_date(self, obj):
        """Returns estimated delivery date as shown in UI"""
        return timezone.now() + timezone.timedelta(days=obj.estimated_days)
    
class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = ['code', 'discount_percentage']
        read_only_fields = ['discount_percentage']


class TicketResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketResponse
        fields = ['id', 'message', 'is_staff_response', 'created_at', 'attachment']
        read_only_fields = ['is_staff_response']

class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = ['id', 'full_name', 'message', 'status', 'created_at', 'updated_at']
        read_only_fields = ['status', 'created_at', 'updated_at']
        
class DashboardCartMetricsSerializer(serializers.Serializer):
    abandoned_rate = serializers.FloatField()
    total_carts = serializers.IntegerField()
    abandoned_carts = serializers.IntegerField()
    period = serializers.CharField()

class DashboardCustomerMetricsSerializer(serializers.Serializer):
    total_customers = serializers.IntegerField()
    active_customers = serializers.IntegerField()
    growth_rate = serializers.FloatField()
    period = serializers.CharField()

class DashboardOrderStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()

class DashboardOrderMetricsSerializer(serializers.Serializer):
    orders_by_status = DashboardOrderStatusSerializer(many=True)
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_orders = serializers.IntegerField()
    period = serializers.CharField()

class DashboardSalesTrendSerializer(serializers.Serializer):
    date = serializers.DateField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    orders = serializers.IntegerField()

class DashboardRecentOrderItemSerializer(serializers.Serializer):
    product_name = serializers.CharField()
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

class DashboardRecentOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_email = serializers.EmailField()
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    items = DashboardRecentOrderItemSerializer(many=True)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ProductVariantImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None

    class Meta:
        model = ProductVariantImage
        fields = ['id', 'image_url', 'is_primary']
    
class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'hex_code']

class ProductSizeSerializer(serializers.ModelSerializer):
    size = SizeSerializer(read_only=True)
    size_id = serializers.PrimaryKeyRelatedField(
        queryset=Size.objects.all(),
        source='size',
        write_only=True
    )
    
    class Meta:
        model = ProductSize
        fields = ['id', 'size', 'size_id']

class ProductColorSerializer(serializers.ModelSerializer):
    color = ColorSerializer(read_only=True)
    color_id = serializers.PrimaryKeyRelatedField(
        queryset=Color.objects.all(),
        source='color',
        write_only=True
    )
    
    class Meta:
        model = ProductColor
        fields = ['id', 'color', 'color_id']



class ProductVariationSerializer(serializers.ModelSerializer):
    images = ProductVariantImageSerializer(many=True, read_only=True)
    variant_image_url = serializers.SerializerMethodField()
    image_files = serializers.ListField(
        child=serializers.FileField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    final_price = serializers.SerializerMethodField()
    
    # Keep these for backward compatibility
    size = SizeSerializer(read_only=True)
    color = ColorSerializer(read_only=True)
    size_id = serializers.PrimaryKeyRelatedField(
        queryset=Size.objects.all(), 
        source='size',
        write_only=True,
        required=False
    )
    color_id = serializers.PrimaryKeyRelatedField(
        queryset=Color.objects.all(), 
        source='color',
        write_only=True,
        required=False
    )
    
    # Add these for multiple sizes and colors
    sizes = SizeSerializer(many=True, read_only=True)
    colors = ColorSerializer(many=True, read_only=True)
    size_ids = serializers.PrimaryKeyRelatedField(
        queryset=Size.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='sizes'
    )
    color_ids = serializers.PrimaryKeyRelatedField(
        queryset=Color.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='colors'
    )

    class Meta:
        model = ProductVariation
        fields = [
            'id', 'variation_type', 'variation', 'price_adjustment',
            'stock_quantity', 'sku', 'is_default', 'images', 'image_files',
            'variant_image_url', 'final_price', 'variant_image',
            # Single size/color (backward compatibility)
            'size', 'size_id', 'color', 'color_id',
            # Multiple sizes/colors (new fields)
            'sizes', 'size_ids', 'colors', 'color_ids'
        ]
    def get_variant_image_url(self, obj):
        return obj.variant_image.url if obj.variant_image else None

    def get_final_price(self, obj):
        # Calculate the final price by adding the base price of the product 
        # and the price adjustment of the variant
        base_price = obj.product.base_price if obj.product else 0
        price_adjustment = obj.price_adjustment if obj.price_adjustment else 0
        return float(base_price) + float(price_adjustment)

    def create(self, validated_data):
        image_files = validated_data.pop('image_files', [])
        variant = super().create(validated_data)
        
        # Handle image uploads
        for index, image_file in enumerate(image_files):
            try:
                # Upload main variant image
                if index == 0:
                    # Direct assignment to CloudinaryField
                    variant.variant_image = image_file
                    variant.save()

                # Create additional variant images
                result = upload(
                    image_file,
                    folder=f'product_variants/{variant.product.id}/{variant.id}/',
                    resource_type='auto'
                )
                ProductVariantImage.objects.create(
                    variant=variant,
                    image=image_file,  # Pass the file directly, not the URL
                    is_primary=(index == 0)
                )
                
            except Exception as e:
                raise serializers.ValidationError(f"Failed to upload image: {str(e)}")
        
        return variant

    def update(self, instance, validated_data):
        image_files = validated_data.pop('image_files', [])
        variant = super().update(instance, validated_data)
        
        if image_files:
            # Optional: Clear existing images
            instance.images.all().delete()
            
            for index, image_file in enumerate(image_files):
                try:
                    # Update main variant image
                    if index == 0:
                        variant.variant_image = image_file
                        variant.save()

                    # Create additional variant images
                    ProductVariantImage.objects.create(
                        variant=variant,
                        image=image_file,  # Pass the file directly
                        is_primary=(index == 0)
                    )
                    
                except Exception as e:
                    raise serializers.ValidationError(f"Failed to upload image: {str(e)}")
        
        return variant

class ProductManagementSerializer(serializers.ModelSerializer):
    # General Information Fields
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), 
        many=True, 
        required=False
    )

    # Add this new field to handle multiple image uploads
    image_files = serializers.ListField(
        child=serializers.FileField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    # Pricing Fields
    base_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False, 
        source='price'
    )
    discount_type = serializers.ChoiceField(
        choices=['percentage', 'fixed'], 
        required=False
    )
    discount_percentage = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False
    )
    vat_amount = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False
    )

    
    variations = ProductVariationSerializer(many=True, required=False)
    variants_count = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    
    is_liked = serializers.SerializerMethodField()
    available_sizes = ProductSizeSerializer(many=True, required=False)
    available_colors = ProductColorSerializer(many=True, required=False)
    variations = ProductVariationSerializer(many=True, required=False)
    

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            try:
                # Use the annotation if it exists
                if hasattr(obj, 'is_in_wishlist'):
                    return obj.is_in_wishlist
                    
                # Otherwise check directly
                return WishlistItem.objects.filter(
                    wishlist__user=request.user,
                    product_id=obj.id  # This is correct
                ).exists()
            except Exception as e:
                print(f"Error checking wishlist status: {e}")
        return False

    class Meta:
        model = Product
        fields = [
            # General Information
            'id', 'name', 'description', 'product_details', 'category', 'category_name', 
            'tags', 'status', 'status_display', 'main_image', 'images',
            'image_files',  'is_featured', 'is_liked', 'available_sizes', 'available_colors',
            'variations',
            # Pricing
            'base_price', 'discount_type', 'discount_percentage', 
            'vat_amount',
            # Inventory
            'sku', 'barcode', 'stock_quantity', 'variations',
            # Shipping
            'is_physical_product', 'weight', 'height', 
            'length', 'width',
            # Additional
            'created_at', 'variants_count'
        ]
        read_only_fields = ['created_at', 'id']
        extra_kwargs = {
            'status': {'required': False, 'default': 'draft'}
        }

    def get_main_image(self, obj):
        if obj.main_image:
            return obj.main_image.url
        return None

    def get_variants_count(self, obj):
        return obj.variations.count() if hasattr(obj, 'variations') else 0

    def get_status_display(self, obj):
        status_mapping = {
            'published': 'Published',
            'draft': 'Draft',
            'inactive': 'Inactive',
            'out_of_stock': 'Low Stock'
        }
        return status_mapping.get(obj.status, obj.status)

    def handle_image_upload(self, image):
        try:
            result = upload(
                image,
                folder='products/',
                resource_type='auto'
            )
            return result['secure_url']
        except Exception as e:
            raise serializers.ValidationError(f"Failed to upload image: {str(e)}")

    def create(self, validated_data):
        # Handle variations and image files
        variations_data = validated_data.pop('variations', [])
        image_files = validated_data.pop('image_files', None)
        
        # Create product
        product = Product.objects.create(**validated_data)
        
        # Create variations
        for variation_data in variations_data:
            ProductVariation.objects.create(
                product=product,
                variation_type=variation_data.get('variation_type'),
                variation=variation_data.get('variation')
            )

        # Handle image uploads if any
        if image_files:
            uploaded_urls = []
            for image_file in image_files:
                url = self.handle_image_upload(image_file)
                uploaded_urls.append(url)
            
            # Update the images JSON field
            current_images = product.images or []
            product.images = current_images + uploaded_urls
            product.save()
        
        return product
    def create(self, validated_data):
        available_sizes_data = validated_data.pop('available_sizes', [])
        available_colors_data = validated_data.pop('available_colors', [])
        variations_data = validated_data.pop('variations', [])
        
        # Create product
        product = Product.objects.create(**validated_data)
        
        # Create available sizes
        for size_data in available_sizes_data:
            ProductSize.objects.create(product=product, **size_data)
        
        # Create available colors
        for color_data in available_colors_data:
            ProductColor.objects.create(product=product, **color_data)
        
        # Create variations
        for variation_data in variations_data:
            ProductVariation.objects.create(product=product, **variation_data)
        
        return product
    
    def update(self, instance, validated_data):
        available_sizes_data = validated_data.pop('available_sizes', [])
        available_colors_data = validated_data.pop('available_colors', [])
        variations_data = validated_data.pop('variations', [])
        
        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Handle sizes (optional: clear and recreate)
        if available_sizes_data:
            instance.available_sizes.all().delete()
            for size_data in available_sizes_data:
                ProductSize.objects.create(product=instance, **size_data)
        
        # Handle colors (optional: clear and recreate)
        if available_colors_data:
            instance.available_colors.all().delete()
            for color_data in available_colors_data:
                ProductColor.objects.create(product=instance, **color_data)
        
        # Handle variations
        if variations_data:
            instance.variations.all().delete()
            for variation_data in variations_data:
                ProductVariation.objects.create(product=instance, **variation_data)
        
        instance.save()
        return instance

    def update(self, instance, validated_data):
        # Handle variations and image files
        variations_data = validated_data.pop('variations', [])
        image_files = validated_data.pop('image_files', None)
        
        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update variations
        instance.variations.all().delete()
        for variation_data in variations_data:
            ProductVariation.objects.create(
                product=instance,
                variation_type=variation_data.get('variation_type'),
                variation=variation_data.get('variation')
            )

        # Handle image uploads if any
        if image_files:
            uploaded_urls = []
            for image_file in image_files:
                url = self.handle_image_upload(image_file)
                uploaded_urls.append(url)
            
            # Update the images JSON field
            current_images = instance.images or []
            instance.images = current_images + uploaded_urls
            
        instance.save()
        return instance

class CarouselItemSerializer(serializers.ModelSerializer):
    """Serializer for carousel items with all fields for admin use"""
    image_url = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CarouselItem
        fields = [
            'id', 'title', 'subtitle', 'button_text', 'button_link',
            'image', 'image_url', 'product', 'product_name', 'order', 'active'
        ]
    
    def get_image_url(self, obj):
        """Get the Cloudinary URL for the image"""
        return obj.image.url if obj.image else None
        
    def get_product_name(self, obj):
        """Get the name of the linked product if any"""
        return obj.product.name if obj.product else None

class CarouselItemPublicSerializer(serializers.ModelSerializer):
    """Lightweight serializer for public carousel display - minimizes payload size"""
    url = serializers.SerializerMethodField()  # Renamed from image_url to match frontend needs

    class Meta:
        model = CarouselItem
        fields = ['id', 'url', 'text']

    def get_url(self, obj):
        """Get the Cloudinary URL for the image"""
        return obj.image.url if obj.image else None
    
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone']

class CustomerCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        
        # Create user if password is provided
        user = None
        if password:
            user = CustomUser.objects.create_user(
                email=validated_data['email'],
                password=password
            )

        # Create customer
        customer = Customer.objects.create(
            user=user,
            **validated_data
        )
        
        return customer