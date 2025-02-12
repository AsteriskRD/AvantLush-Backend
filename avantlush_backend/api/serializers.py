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
    Customer
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
            'is_featured', 'sku', 'status', 'created_at', 'updated_at',
            'rating', 'num_ratings'
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
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'product_name', 'product_price', 'stock_status']
        
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at', 'updated_at']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'method', 'amount', 'status', 'created_at']
        
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_sku = serializers.CharField(source='product.sku')
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_sku', 'quantity', 
                 'unit_price', 'total_price', 'variants']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)
    customer_email = serializers.EmailField(source='user.email', read_only=True)
    customer_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer_email', 'customer_name',
            'items', 'total', 'status', 'status_display', 'payment',
            'shipping_address', 'billing_address', 'created_at', 
            'updated_at', 'notes', 'payment_type', 'order_type',
            'order_date', 'order_time'  # Added these fields from OrderDetailSerializer
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
            'billing_address', 'notes', 'payment_type', 'order_type',
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
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'products']

class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = ['id', 'wishlist', 'product', 'added_at']

class WishlistNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistNotification
        fields = ['id', 'notification_type', 'message', 'is_read', 'created_at']
        read_only_fields = ['created_at']


class ProductRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRecommendation
        fields = ['id', 'product', 'recommended_product', 'score']


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
    responses = TicketResponseSerializer(many=True, read_only=True)
    
    class Meta:
        model = SupportTicket
        fields = ['id', 'subject', 'message', 'status', 'priority', 'order', 
                 'created_at', 'updated_at', 'responses']
        read_only_fields = ['created_at', 'updated_at']

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

class ProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariation  # Assuming you'll add this model
        fields = ['variation_type', 'variation']

class ProductManagementSerializer(serializers.ModelSerializer):
    # General Information Fields
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), 
        many=True, 
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

    # Inventory Fields
    barcode = serializers.CharField(required=False, allow_blank=True)
    variations = ProductVariationSerializer(many=True, required=False)

    # Shipping Fields
    is_physical_product = serializers.BooleanField(default=True)
    weight = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False
    )
    height = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False
    )
    length = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False
    )
    width = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False
    )

    # Additional Fields
    variants_count = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            # General Information
            'id', 'name', 'description', 'category', 'category_name', 
            'tags', 'status', 'status_display', 'main_image', 'images',
        

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

    def get_variants_count(self, obj):
        # Implement based on your variation model
        return obj.variations.count() if hasattr(obj, 'variations') else 0

    def get_status_display(self, obj):
        status_mapping = {
            'published': 'Published',
            'draft': 'Draft',
            'inactive': 'Inactive',
            'out_of_stock': 'Low Stock'
        }
        return status_mapping.get(obj.status, obj.status)

    def create(self, validated_data):
        # Handle variations during product creation
        variations_data = validated_data.pop('variations', [])
        
        # Create product
        product = Product.objects.create(**validated_data)
        
        # Create variations
        for variation_data in variations_data:
            ProductVariation.objects.create(
                product=product,
                variation_type=variation_data.get('variation_type'),
                variation=variation_data.get('variation')
            )
        
        return product

    def update(self, instance, validated_data):
        # Handle variations during product update
        variations_data = validated_data.pop('variations', [])
        
        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update variations
        # First, clear existing variations
        instance.variations.all().delete()
        
        # Create new variations
        for variation_data in variations_data:
            ProductVariation.objects.create(
                product=instance,
                variation_type=variation_data.get('variation_type'),
                variation=variation_data.get('variation')
            )
        
        return instance
        
class ProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariation  
        fields = ['variation_type', 'variation']
        
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

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