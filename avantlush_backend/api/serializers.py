from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from dj_rest_auth.registration.serializers import SocialLoginSerializer, RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
import re
from .utils import VALID_COUNTRY_CODES, validate_phone_format, format_phone_number
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
    models,
    Customer,
    CarouselItem,
    Size,
    Color,
    ProductSize,
    ProductColor,
    Wishlist,
    WishlistItem,
    ProductRecommendation,
    Review,
    ReviewTag,
    ReviewHelpfulVote,
    PromoCode,
    ShippingMethod
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
    location = serializers.CharField(required=False, default='Nigeria')

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Google token is required")
        return value

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
    """Detailed customer serializer matching dashboard requirements"""
    status = serializers.SerializerMethodField()
    orders_count = serializers.IntegerField(read_only=True)
    balance = serializers.SerializerMethodField()
    recent_orders = serializers.SerializerMethodField()
    
    # Additional fields for dashboard
    customer_id = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    last_transaction = serializers.SerializerMethodField()
    last_online = serializers.SerializerMethodField()
    total_orders_value = serializers.SerializerMethodField()
    abandoned_cart_count = serializers.SerializerMethodField()
    order_status_breakdown = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'customer_id', 'name', 'email', 'phone', 'status', 'address',
            'orders_count', 'balance', 'total_orders_value', 'abandoned_cart_count',
            'order_status_breakdown', 'last_transaction', 'last_online',
            'created_at', 'recent_orders'
        ]
    
    def get_status(self, obj):
        if obj.user:
            return 'active' if obj.user.is_active else 'blocked'
        return 'active'
    
    def get_customer_id(self, obj):
        """Generate customer ID like ID-011221"""
        return f"ID-{str(obj.id).zfill(6)}"
    
    def get_balance(self, obj):
        """Get customer's current balance from orders"""
        from .models import Order
        from django.db.models import Sum
        if not obj.user:
            return 0
            
        total_paid = Order.objects.filter(
            user=obj.user, 
            payment_status='PAID'
        ).aggregate(total=Sum('total'))['total'] or 0
        
        total_orders = Order.objects.filter(
            user=obj.user
        ).aggregate(total=Sum('total'))['total'] or 0
        
        return total_paid - total_orders
    
    def get_address(self, obj):
        """Get customer's address from Address model"""
        if obj.user:
            address = obj.user.address_set.filter(is_default=True).first()
            if address:
                return f"{address.street_address}, {address.city}, {address.state} {address.zip_code}, {address.country}"
        return "No address provided"
    
    def get_last_transaction(self, obj):
        """Get last order date"""
        from .models import Order
        if not obj.user:
            return "No transactions"
        last_order = Order.objects.filter(user=obj.user).order_by('-created_at').first()
        if last_order:
            return last_order.created_at.strftime("%d %B %Y")
        return "No transactions"
    
    def get_last_online(self, obj):
        """Get last login time"""
        if obj.user and obj.user.last_login:
            from django.utils import timezone
            now = timezone.now()
            diff = now - obj.user.last_login
            
            if diff.days == 0:
                if diff.seconds < 3600:
                    return f"{diff.seconds // 60} minutes ago"
                else:
                    return f"{diff.seconds // 3600} hours ago"
            elif diff.days == 1:
                return "1 day ago"
            else:
                return f"{diff.days} days ago"
        return "Never logged in"
    
    def get_total_orders_value(self, obj):
        """Get total value of all orders"""
        from .models import Order
        from django.db.models import Sum
        if not obj.user:
            return "0.00"
        total = Order.objects.filter(user=obj.user).aggregate(total=Sum('total'))['total'] or 0
        return f"{total:.2f}"
    
    def get_abandoned_cart_count(self, obj):
        """Get count of abandoned carts"""
        from .models import Cart
        from django.db.models import F
        if obj.user:
            abandoned_carts = Cart.objects.filter(
                user=obj.user,
                items__isnull=False
            ).exclude(
                user__orders__created_at__gte=F('created_at')
            ).distinct().count()
            return abandoned_carts
        return 0
    
    def get_order_status_breakdown(self, obj):
        """Get breakdown of orders by status"""
        from .models import Order
        from django.db.models import Count
        
        if not obj.user:
            return {
                'all_orders': 0,
                'pending': 0,
                'processing': 0,
                'shipped': 0,
                'delivered': 0,
                'cancelled': 0,
                'returned': 0,
                'damaged': 0
            }
        
        breakdown = Order.objects.filter(user=obj.user).values('status').annotate(
            count=Count('id')
        )
        
        status_counts = {
            'all_orders': 0,
            'pending': 0,
            'processing': 0,
            'shipped': 0,
            'delivered': 0,
            'cancelled': 0,
            'returned': 0,
            'damaged': 0
        }
        
        for item in breakdown:
            status = item['status'].lower()
            count = item['count']
            status_counts['all_orders'] += count
            
            if status == 'pending':
                status_counts['pending'] = count
            elif status == 'processing':
                status_counts['processing'] = count
            elif status == 'shipped':
                status_counts['shipped'] = count
            elif status == 'delivered':
                status_counts['delivered'] = count
            elif status == 'cancelled':
                status_counts['cancelled'] = count
            elif status == 'returned':
                status_counts['returned'] = count
            elif status == 'damaged':
                status_counts['damaged'] = count
        
        return status_counts
    
    def get_recent_orders(self, obj):
        if not obj.user:
            return []
        recent_orders = Order.objects.filter(user=obj.user).order_by('-created_at')[:5]
        return OrderSerializer(recent_orders, many=True).data

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

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
   
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
    # Size and color serializers
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
    quantity_left = serializers.SerializerMethodField(read_only=True)  # New field

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'quantity', 'product_name', 'product_price',
            'stock_status', 'product_image', 'size', 'color', 'size_id', 'color_id',
            'quantity_left'  # Add new field here
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['cart_item_id'] = representation.pop('id')
        
        # Ensure size and color are properly included
        if instance.size:
            representation['size'] = SizeSerializer(instance.size).data
        else:
            representation['size'] = None
            
        if instance.color:
            representation['color'] = ColorSerializer(instance.color).data
        else:
            representation['color'] = None
            
        return representation
    
    def get_product_image(self, obj):
        # Check if product has a main image
        if obj.product.main_image:
            return obj.product.main_image.url
        
        # If no main image, check if it has any images in the images list
        elif obj.product.images and len(obj.product.images) > 0:
            return obj.product.images[0]  # Return the first image URL
            
        return None  # Return None if no images are available

    def get_quantity_left(self, obj):
        # Return the current stock left for this product
        return obj.product.stock_quantity
    
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
    products_display_string = serializers.SerializerMethodField()
    
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
            'items', 'products_display_string', 'total', 'status', 'status_display', 'payment', 'payments',
            'shipping_address', 'created_at', 'estimated_delivery_date',
            'updated_at', 'note', 'payment_type', 'order_type',
            'order_date', 'order_time'
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']

    def get_products_display_string(self, obj):
        items = obj.items.all()  # Get all related order items
        if not items:
            return "No products"
        
        first_item_product_name = items[0].product.name
        
        if len(items) == 1:
            return first_item_product_name
        else:
            others_count = len(items) - 1
            return f"{first_item_product_name} +{others_count} other product{'s' if others_count > 1 else ''}"
    
    def get_customer_name(self, obj):
        if obj.user.first_name or obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return obj.user.email
    
    def get_status_display(self, obj):
        return obj.get_status_display()


class FlatOrderItemSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number')
    customer_email = serializers.EmailField(source='order.user.email')
    customer_name = serializers.SerializerMethodField()
    status = serializers.CharField(source='order.status')
    status_display = serializers.SerializerMethodField()
    total = serializers.DecimalField(source='subtotal', max_digits=10, decimal_places=2)
    created_at = serializers.DateTimeField(source='order.created_at')
    updated_at = serializers.DateTimeField(source='order.updated_at')
    order_date = serializers.DateField(source='order.order_date')
    order_time = serializers.TimeField(source='order.order_time')
    shipping_address = serializers.CharField(source='order.shipping_address')
    order_type = serializers.CharField(source='order.order_type')
    payment_type = serializers.CharField(source='order.payment_type')
    estimated_delivery_date = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='product.name')
    product_image = serializers.SerializerMethodField()
    
    def get_customer_name(self, obj):
        if obj.order.user.first_name or obj.order.user.last_name:
            return f"{obj.order.user.first_name} {obj.order.user.last_name}".strip()
        return obj.order.user.email
    
    def get_status_display(self, obj):
        return obj.order.get_status_display()
    
    def get_estimated_delivery_date(self, obj):
        # Look for tracking entry with "Estimated Delivery" status
        estimated_delivery = obj.order.tracking_history.filter(status="Estimated Delivery").first()
        
        if estimated_delivery:
            # Extract date from description using regex
            import re
            match = re.search(r'by ([A-Za-z]+, [A-Za-z]+ \d+, \d{4})', estimated_delivery.description)
            if match:
                return match.group(1)
        
        # If no specific tracking entry, calculate based on order type and date
        if obj.order.order_type == 'EXPRESS':
            days = 2
        else:  # STANDARD
            days = 5
            
        from django.utils import timezone
        from datetime import timedelta
        
        base_date = obj.order.created_at
        delivery_date = base_date + timedelta(days=days)
        
        # Format the date nicely
        return delivery_date.strftime("%A, %B %d, %Y")
    
    def get_product_image(self, obj):
        # Get main image URL
        if obj.product.main_image:
            return obj.product.main_image.url
        elif obj.product.images and len(obj.product.images) > 0:
            return obj.product.images[0]
        return None
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'order_number', 'customer_email', 'customer_name',
            'product', 'product_name', 'quantity', 'price', 'total', 'status', 
            'status_display', 'shipping_address', 'created_at', 'estimated_delivery_date',
            'updated_at', 'payment_type', 'order_type', 'product_image',
            'order_date', 'order_time'
        ]

class ProductForOrderSerializer(serializers.ModelSerializer):
    """Simplified product serializer for order creation"""
    formatted_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'price', 'formatted_price', 
                 'stock_quantity', 'main_image']
    
    def get_formatted_price(self, obj):
        return f"${obj.price:,.2f}"
    
class OrderCreateEnhancedSerializer(serializers.ModelSerializer):
    """Enhanced order creation serializer"""
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        help_text="List of order items with product_id, quantity, price"
    )
    customer_id = serializers.IntegerField(write_only=True, required=False)
    
    # Add these fields to match your UI
    order_date = serializers.DateField(required=False)
    order_time = serializers.TimeField(required=False)
    
    class Meta:
        model = Order
        fields = [
            'customer_id', 'items', 'payment_type', 'order_type', 
            'status', 'order_date', 'order_time', 'note',
            'shipping_address', 'shipping_city', 'shipping_state',
            'shipping_country', 'shipping_zip'
        ]
    
    def validate_items(self, items):
        """Validate order items"""
        if not items:
            raise serializers.ValidationError("Order must have at least one item")
        
        for item in items:
            if 'product_id' not in item:
                raise serializers.ValidationError("Each item must have a product_id")
            if 'quantity' not in item or item['quantity'] <= 0:
                raise serializers.ValidationError("Each item must have a valid quantity")
                
            # Check if product exists and has enough stock
            try:
                product = Product.objects.get(id=item['product_id'])
                if product.stock_quantity < item['quantity']:
                    raise serializers.ValidationError(
                        f"Not enough stock for {product.name}. Available: {product.stock_quantity}"
                    )
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with ID {item['product_id']} does not exist")
        
        return items
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        customer_id = validated_data.pop('customer_id', None)
        
        # Set customer if provided
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
                validated_data['customer'] = customer
                if customer.user:
                    validated_data['user'] = customer.user
            except Customer.DoesNotExist:
                raise serializers.ValidationError("Customer not found")
        
        # Set current user if no customer user
        if 'user' not in validated_data:
            validated_data['user'] = self.context['request'].user
        
        # Create order
        order = Order.objects.create(**validated_data)
        
        # Create order items and calculate totals
        subtotal = 0
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            quantity = item_data['quantity']
            
            # Use provided price or product price
            unit_price = item_data.get('price', product.price)
            
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=unit_price
            )
            subtotal += order_item.subtotal
            
            # Update product stock
            product.stock_quantity -= quantity
            product.save()
        
        # Update order totals
        order.subtotal = subtotal
        order.save()  # This will trigger total calculation in the model
        
        return order
        
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
    name = serializers.CharField(write_only=True, required=True)  # For user's name input
    title = serializers.CharField(required=True)  # For review title
    content = serializers.CharField(required=True)  # For review details
    rating = serializers.IntegerField(min_value=1, max_value=5, required=True)
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
            'id', 'product', 'user_email', 'name', 'title', 'rating', 'content',
            'tags', 'tag_ids', 'helpful_count', 'is_helpful',
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
        name = validated_data.pop('name', None)
        
        # Update user's name if provided
        if name and self.context['request'].user:
            user = self.context['request'].user
            user.first_name = name
            user.save()

        if 'user' in validated_data:
            validated_data.pop('user')
        
        # Create the review
        review = Review.objects.create(
            user=self.context['request'].user,
            **validated_data
        )
        
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
    converted_carts = serializers.IntegerField()
    abandonment_reasons = serializers.DictField(required=False)
    period = serializers.CharField()

class DashboardCustomerMetricsSerializer(serializers.Serializer):
    new_customers = serializers.IntegerField()
    new_customer_growth = serializers.FloatField()
    total_customers = serializers.IntegerField()
    active_customers = serializers.IntegerField()
    active_customer_growth = serializers.FloatField()
    returning_customers = serializers.IntegerField()
    period = serializers.CharField()

class DashboardOrderStatusBreakdownSerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)

class DashboardOrderMetricsSerializer(serializers.Serializer):
    status_breakdown = DashboardOrderStatusBreakdownSerializer(many=True)
    total_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_order_value = serializers.FloatField()
    daily_trend = serializers.ListField(required=False)
    status_filter = serializers.CharField(allow_null=True, required=False)
    period = serializers.CharField()

# New serializer for the overview endpoint
class DashboardOverviewSerializer(serializers.Serializer):
    abandoned_cart = serializers.DictField()
    customers = serializers.DictField()
    active_customers = serializers.DictField()
    orders = serializers.DictField()
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

class DashboardRecentOrderItemSerializer(serializers.Serializer):
    """Safe serializer for recent order items"""
    id = serializers.IntegerField()
    order_number = serializers.CharField()
    customer_name = serializers.CharField()
    customer_email = serializers.EmailField()
    total = serializers.FloatField()
    status = serializers.CharField()
    status_display = serializers.CharField()
    created_at = serializers.CharField()  # Already formatted as ISO string
    product_image = serializers.URLField(allow_null=True)
    items_count = serializers.IntegerField()
    first_product_name = serializers.CharField(allow_null=True)

class DashboardRecentOrdersResponseSerializer(serializers.Serializer):
    """Response serializer for recent orders endpoint"""
    recent_orders = DashboardRecentOrderItemSerializer(many=True)
    total_count = serializers.IntegerField()
    error = serializers.CharField(required=False)

class DashboardSummaryItemSerializer(serializers.Serializer):
    """Serializer for individual summary items"""
    count = serializers.IntegerField()
    label = serializers.CharField()

class DashboardSummaryResponseSerializer(serializers.Serializer):
    """Response serializer for dashboard summary"""
    summary = serializers.DictField()
    period = serializers.CharField()
    last_updated = serializers.CharField()
    error = serializers.CharField(required=False)

class ProductTableSerializer(serializers.ModelSerializer):
    """
    Serializer for product table display
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    variant_count = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    formatted_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category_name', 'variant_count',
            'stock_quantity', 'stock_status', 'price', 'formatted_price',
            'status', 'created_at', 'main_image', 'is_featured'
        ]
    
    def get_variant_count(self, obj):
        return obj.variations.count()
    
    def get_stock_status(self, obj):
        if obj.stock_quantity == 0:
            return {'status': 'out_of_stock', 'label': 'Out of Stock', 'color': 'red'}
        elif obj.stock_quantity <= 10:
            return {'status': 'low_stock', 'label': 'Low Stock', 'color': 'orange'}
        else:
            return {'status': 'in_stock', 'label': 'In Stock', 'color': 'green'}
    
    def get_formatted_price(self, obj):
        return f"${obj.price:,.2f}"

class ProductVariationSerializer(serializers.ModelSerializer):
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
            'stock_quantity', 'sku', 'is_default',
             'final_price', 
            # Single size/color (backward compatibility)
            'size', 'size_id', 'color', 'color_id',
            # Multiple sizes/colors (new fields)
            'sizes', 'size_ids', 'colors', 'color_ids'
        ]
    
    def get_final_price(self, obj):
        # Calculate the final price by adding the base price of the product 
        # and the price adjustment of the variant
        base_price = obj.product.base_price if obj.product else 0
        price_adjustment = obj.price_adjustment if obj.price_adjustment else 0
        return float(base_price) + float(price_adjustment)

    def create(self, validated_data):
        variant = super().create(validated_data)
        return variant

    def update(self, instance, validated_data):
        # Simply call the super method to update the instance
        variant = super().update(instance, validated_data)
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
    discount_value = serializers.DecimalField(
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
    added_date_formatted = serializers.SerializerMethodField() # For "Added" column
    main_image = serializers.SerializerMethodField()
    
    is_liked = serializers.SerializerMethodField()
    available_sizes = ProductSizeSerializer(many=True, required=False)
    available_colors = ProductColorSerializer(many=True, required=False)
    all_images = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            # General Information
            'id', 'name', 'description', 'product_details', 'category', 'category_name', 
            'tags', 'status', 'status_display', 'main_image', 'images',
            'image_files', 'is_featured', 'is_liked', 'available_sizes', 'available_colors',
            'variations',
            # Pricing
            'base_price', 'discount_type', 'discount_value', 
            'vat_amount',
            # Inventory
            'sku', 'barcode', 'stock_quantity', 'variations',
            # Shipping
            'is_physical_product', 'weight', 'height', 
            'length', 'width',
            # Additional
            'created_at', 'added_date_formatted', 'variants_count',
            # Don't forget to add the all_images field here
            'all_images'
        ]
        read_only_fields = ['created_at', 'id', 'added_date_formatted']
        extra_kwargs = {
            'status': {'required': False, 'default': 'draft'}
        }

    def get_all_images(self, obj):
        """Collect all product images into a single structure"""
        result = {
            'main_image': None,
            'gallery': [],
        }
        
        # Add main image
        if obj.main_image:
            result['main_image'] = obj.main_image.url
            # Also add it to the gallery as the first item
            result['gallery'] = [obj.main_image.url]
        
        # Add additional gallery images from JSONField
        if obj.images:
            # If we already have a main image in gallery, extend the list
            # Otherwise assign directly
            if result['gallery']:
                result['gallery'].extend(obj.images)
            else:
                result['gallery'] = obj.images
                
        return result        
        # Add variant images
#      for variant in obj.variations.all():
#           variant_id = str(variant.id)
#            result['variants'][variant_id] = []
            
            # Add variant's main image
#            if variant.variant_image:
#                result['variants'][variant_id].append(variant.variant_image.url)
#            
#            # Add variant's additional images
#            for img in variant.images.all():
#                if img.image:
#                    result['variants'][variant_id].append(img.image.url)
            
        return result

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
                    product_id=obj.id
                ).exists()
            except Exception as e:
                print(f"Error checking wishlist status: {e}")
        return False

    def get_main_image(self, obj):
        if obj.main_image:
            return obj.main_image.url
        return None

    def get_variants_count(self, obj):
        return obj.variations.count() if hasattr(obj, 'variations') else 0

    def get_status_display(self, obj):
        # Using the model's get_status_display method is preferred if it exists and is accurate.
        # Assuming Product model has get_X_display() for choice fields.
        # Or, implement more detailed logic based on UI:
        if obj.status == 'published':
            return 'Published'
        elif obj.status == 'draft':
            return 'Draft'
        # The UI shows "Low Stock" for stock 0, or if status is 'low_stock' or 'out_of_stock'
        elif obj.stock_quantity == 0 or obj.status in ['low_stock', 'out_of_stock']:
            return 'Low Stock'
        # Fallback to the model's display name for other statuses
        return obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status

    def get_added_date_formatted(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%d %b %Y')
        return None

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
        # Handle variations, sizes, colors, and image files
        variations_data = validated_data.pop('variations', [])
        available_sizes_data = validated_data.pop('available_sizes', [])
        available_colors_data = validated_data.pop('available_colors', [])
        image_files = validated_data.pop('image_files', None)
        
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

        # Handle image uploads if any
        if image_files:
            uploaded_urls = []
            for image_file in image_files:
                url = self.handle_image_upload(image_file)
                uploaded_urls.append(url)
            
            # Update the images JSON field
            product.images = uploaded_urls
            product.save()
        
        return product
    
    def update(self, instance, validated_data):
        # Handle variations, sizes, colors, and image files
        variations_data = validated_data.pop('variations', [])
        available_sizes_data = validated_data.pop('available_sizes', [])
        available_colors_data = validated_data.pop('available_colors', [])
        image_files = validated_data.pop('image_files', None)
        
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
    

class CloverWebhookSerializer(serializers.Serializer):
    """Serializer for validating Clover webhook data"""
    type = serializers.CharField(help_text="Webhook event type")
    status = serializers.CharField(help_text="Payment status (APPROVED, DECLINED, CANCELLED)")
    data = serializers.CharField(help_text="Checkout session ID")
    id = serializers.CharField(required=False, help_text="Payment ID")
    timestamp = serializers.IntegerField(required=False, help_text="Event timestamp")
    amount = serializers.IntegerField(required=False, help_text="Payment amount in cents")
    currency = serializers.CharField(required=False, default="USD", help_text="Payment currency")
    
    def validate_status(self, value):
        """Validate webhook status"""
        valid_statuses = ['APPROVED', 'DECLINED', 'CANCELLED', 'PENDING']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Must be one of: {valid_statuses}")
        return value

class CloverHostedCheckoutRequestSerializer(serializers.Serializer):
    """Serializer for Clover hosted checkout creation request"""
    order_id = serializers.IntegerField(help_text="Order ID to create checkout for")
    success_url = serializers.URLField(required=False, help_text="Success redirect URL")
    failure_url = serializers.URLField(required=False, help_text="Failure redirect URL")
    
    def validate_order_id(self, value):
        """Validate that order exists and belongs to user"""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required")
        
        try:
            order = Order.objects.get(id=value, user=request.user)
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found or access denied")

class CloverHostedCheckoutResponseSerializer(serializers.Serializer):
    """Serializer for Clover hosted checkout creation response"""
    success = serializers.BooleanField()
    checkout_url = serializers.URLField(required=False)
    session_id = serializers.CharField(required=False)
    expires_at = serializers.DateTimeField(required=False)
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)

class CloverPaymentStatusSerializer(serializers.Serializer):
    """Serializer for Clover payment status response"""
    order_id = serializers.IntegerField()
    payment_status = serializers.CharField()
    order_status = serializers.CharField()
    session_id = serializers.CharField(required=False)
    payment_id = serializers.CharField(required=False)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)

class CustomerSimpleSerializer(serializers.ModelSerializer):
    """Simple customer serializer for dropdowns"""
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'display_name']
    
    def get_display_name(self, obj):
        return f"{obj.name} ({obj.email})"

class CarouselItemSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CarouselItem
        fields = ['id', 'text', 'image', 'image_url', 'active', 'order', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'image_url']

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None
    
class CarouselItemPublicSerializer(serializers.ModelSerializer):
    """Lightweight serializer for public carousel display - minimizes payload size"""
    url = serializers.SerializerMethodField()  # Renamed from image_url to match frontend needs

    class Meta:
        model = CarouselItem
        fields = ['id', 'url', 'text']

    def get_url(self, obj):
        """Get the Cloudinary URL for the image"""
        return obj.image.url if obj.image else None
    
""""    
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
"""


# Add these serializers to your serializers.py file

class CustomerSerializer(serializers.ModelSerializer):
    """Simple customer serializer for listing"""
    status = serializers.SerializerMethodField()
    orders_count = serializers.IntegerField(read_only=True)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'status', 'orders_count', 'balance', 'created_at']
    
    def get_status(self, obj):
        # If you add status field to model, use: return obj.status
        # For now, using user.is_active:
        if obj.user:
            return 'active' if obj.user.is_active else 'blocked'
        return 'active'

class CustomerUpdateSerializer(serializers.ModelSerializer):
    """Serializer specifically for updating customer details"""
    status = serializers.ChoiceField(choices=Customer.STATUS_CHOICES, required=False)
    
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'country_code', 'local_phone_number', 'status']
    
    def validate(self, data):
        country_code = data.get('country_code')
        local_phone_number = data.get('local_phone_number')

        # Only validate if both country_code and local_phone_number are provided
        if country_code and local_phone_number:
            from .utils import validate_phone_format
            is_valid, error_message = validate_phone_format(country_code, local_phone_number)
            if not is_valid:
                raise serializers.ValidationError({'phone_number': error_message})
        elif country_code and not local_phone_number:
            raise serializers.ValidationError({'local_phone_number': 'Phone number is required when country code is provided.'})
        elif local_phone_number and not country_code:
            raise serializers.ValidationError({'country_code': 'Country code is required when phone number is provided.'})
            
        return data
    
    def update(self, instance, validated_data):
        # Update basic fields
        if 'name' in validated_data:
            instance.name = validated_data['name']
        
        if 'phone' in validated_data:
            instance.phone = validated_data['phone']
        
        if 'country_code' in validated_data:
            instance.country_code = validated_data['country_code']
        
        if 'local_phone_number' in validated_data:
            instance.local_phone_number = validated_data['local_phone_number']
        
        # Handle status update (this affects the linked user account)
        if 'status' in validated_data:
            new_status = validated_data['status']
            if instance.user:
                # Update user's is_active based on customer status
                # Use update_fields to prevent infinite signal loops
                instance.user.is_active = (new_status == 'active')
                instance.user.save(update_fields=['is_active'])
        
        # Save customer with update_fields to prevent infinite signal loops
        update_fields = []
        for field in validated_data.keys():
            if field in ['name', 'phone', 'country_code', 'local_phone_number', 'status']:
                update_fields.append(field)
        
        if update_fields:
            instance.save(update_fields=update_fields)
        
        return instance

class CustomerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new customers"""
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    create_user_account = serializers.BooleanField(default=False, write_only=True)
    country_code = serializers.CharField(max_length=5, required=False, allow_blank=True, allow_null=True)
    local_phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    address = AddressSerializer(required=False, write_only=True, allow_null=True)
    
    class Meta:
        model = Customer
        fields = [
            'name', 'email', 'country_code', 'local_phone_number', 'address',
            'password', 'create_user_account'
        ]
        # Note: 'phone' field is removed as it will be auto-populated by the model's save() method.

    def validate(self, data):
        country_code = data.get('country_code')
        local_phone_number = data.get('local_phone_number')

        # Only validate if both country_code and local_phone_number are provided
        if country_code and local_phone_number:
            from .utils import validate_phone_format # Import here to avoid circular issues
            is_valid, error_message = validate_phone_format(country_code, local_phone_number)
            if not is_valid:
                raise serializers.ValidationError({'phone_number': error_message})
        elif country_code and not local_phone_number:
            raise serializers.ValidationError({'local_phone_number': 'Phone number is required when country code is provided.'})
        elif local_phone_number and not country_code:
            raise serializers.ValidationError({'country_code': 'Country code is required when phone number is provided.'})
            
        return data
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        create_user_account = validated_data.pop('create_user_account', False)
        address_data = validated_data.pop('address', None)
        
        # Create customer
        customer = Customer.objects.create(**validated_data)
        
        # Optionally create user account
        if create_user_account and password:
            # Ensure email is unique for CustomUser
            if CustomUser.objects.filter(email=customer.email).exists():
                # If an admin is creating a customer for an existing user,
                # try to link them if the customer isn't already linked.
                existing_user = CustomUser.objects.get(email=customer.email)
                if not customer.user:
                    customer.user = existing_user
            else:
                user = CustomUser.objects.create_user(
                    email=customer.email,
                    password=password,
                    # Attempt to get first_name and last_name from customer.name
                    # This part might need adjustment based on how names are typically entered.
                    first_name=customer.name.split(' ')[0] if ' ' in customer.name else customer.name,
                    last_name=' '.join(customer.name.split(' ')[1:]) if ' ' in customer.name else ''
                )
                customer.user = user
            customer.save()

        # Optionally create address if address_data is provided and user exists
        if address_data and customer.user:
            # Ensure all required fields for AddressSerializer are present or have defaults
            # The AddressSerializer itself will validate the fields.
            # We pass customer.user to link the address to the user.
            Address.objects.create(user=customer.user, **address_data)
            # If you want to set this as the default address, you might add:
            # Address.objects.filter(user=customer.user).update(is_default=False)
            # address_instance.is_default = True
            # address_instance.save()
            # However, this logic is usually handled in a dedicated "set default address" endpoint.

        return customer

class ChartDataPointSerializer(serializers.Serializer):
    """Serializer for a single data point in a chart (e.g., date and value)."""
    date = serializers.DateField() # Could also be DateTimeField if time is relevant
    value = serializers.DecimalField(max_digits=12, decimal_places=2) # Adjust precision as needed

class SummaryChartResponseSerializer(serializers.Serializer):
    """Serializer for the overall response of the summary chart data."""
    chart_data = ChartDataPointSerializer(many=True)
    metric_label = serializers.CharField()
    period_label = serializers.CharField()
    # You could add total_value_for_period here if needed
    # total_value_for_period = serializers.DecimalField(max_digits=15, decimal_places=2)