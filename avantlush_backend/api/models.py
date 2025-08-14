from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model
import uuid


User = settings.AUTH_USER_MODEL
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    google_id = models.CharField(max_length=100, blank=True, null=True)
    # --- Add these fields for proper name handling ---
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()

    def __str__(self):
        return self.email

class WaitlistEntry(models.Model):
    email = models.EmailField(unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class EmailVerificationToken(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Verification token for {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)
    @property
    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True)
    photo = CloudinaryField('image', folder='profiles/', null=True, blank=True)  # Profile photo using Cloudinary
    updated_at = models.DateTimeField(auto_now=True)
    country_code = models.CharField(max_length=4, null=True, blank=True)
    def __str__(self):
        return f"Profile for {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.user.get_full_name() or self.user.email
        super().save(*args, **kwargs)

class PasswordResetToken(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()




class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    
    class Meta:
        verbose_name_plural = 'categories'
    
    def __str__(self):
        
        return self.name

class Product(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('published', 'Published'),
        ('draft', 'Draft'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock')
    ]
    
    # Basic fields
    name = models.CharField(max_length=255)
    description = models.TextField()
    product_details = models.JSONField(default=list, blank=True, help_text="List of product details/features as bullet points")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    images = models.JSONField(default=list)
    stock_quantity = models.PositiveIntegerField(default=0)
    slug = models.SlugField(max_length=200, unique=True)
    is_featured = models.BooleanField(default=False)
    sku = models.CharField(max_length=100, unique=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    num_ratings = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Image field
    main_image = CloudinaryField('image', null=True, blank=True, folder='products/')
    image_uploads = CloudinaryField('image', folder='products/variants/', blank=True, null=True)
    # Category and relations
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name='products')
    tags = models.ManyToManyField('Tag', blank=True)
    
    # Pricing fields
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_type = models.CharField(max_length=20, choices=[
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], null=True, blank=True)
    discount_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, 
                                   help_text="Enter discount amount (percentage or fixed value based on discount type)")
    vat_amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Inventory fields
    barcode = models.CharField(max_length=100, null=True, blank=True)
    
    # Shipping fields
    is_physical_product = models.BooleanField(default=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
    def get_similar_products(self, limit=4):
        """Get similar products based on category and price range"""
        price_range = 0.2  # 20% above and below
        return Product.objects.filter(
            category=self.category,
            status='active',
            price__gte=self.price * (1 - price_range),
            price__lte=self.price * (1 + price_range)
        ).exclude(id=self.id)[:limit]

    def get_complementary_products(self, limit=4):
        """Get products that are commonly bought together"""
        return Product.objects.filter(
            orderitem__order__items__product=self
        ).exclude(id=self.id).annotate(
            purchase_count=models.Count('id')
        ).order_by('-purchase_count')[:limit]
    
    def sync_available_sizes(self):
        """
        Synchronize available sizes for the product based on its variations
        """
        # Get all sizes from variations
        variation_sizes = set()
        for variation in self.variations.all():
            # Add sizes from ManyToMany relationship
            variation_sizes.update(size.id for size in variation.sizes.all())
            # Add size from ForeignKey relationship if exists
            if variation.size:
                variation_sizes.add(variation.size.id)
        
        # Clear existing product sizes
        ProductSize.objects.filter(product=self).delete()
        
        # Create new product sizes
        for size_id in variation_sizes:
            try:
                size = Size.objects.get(id=size_id)
                ProductSize.objects.create(product=self, size=size)
            except Size.DoesNotExist:
                pass
        
        # Update available_sizes field if you're using it (seems to be a JSONField)
        self.available_sizes = list(variation_sizes)
        self.save(update_fields=['available_sizes'])

def sync_available_colors(self):
    """
    Synchronize available colors for the product based on its variations
    """
    # Get all colors from variations
    variation_colors = set()
    for variation in self.variations.all():
        # Add colors from ManyToMany relationship
        variation_colors.update(color.id for color in variation.colors.all())
        # Add color from ForeignKey relationship if exists
        if variation.color:
            variation_colors.add(variation.color.id)
    
    # Clear existing product colors
    ProductColor.objects.filter(product=self).delete()
    
    # Create new product colors
    for color_id in variation_colors:
        try:
            color = Color.objects.get(id=color_id)
            ProductColor.objects.create(product=self, color=color)
        except Color.DoesNotExist:
            pass
    
    # Update available_colors field if you're using it (seems to be a JSONField)
    self.available_colors = list(variation_colors)
    self.save(update_fields=['available_colors'])

class ProductView(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']

class Size(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=7, blank=True, null=True, help_text="Hexadecimal color code (e.g., #FF5733)")
    
    def __str__(self):
        return self.name
    

class ProductVariation(models.Model):
    product = models.ForeignKey(Product, related_name='variations', on_delete=models.CASCADE)
    variation_type = models.CharField(max_length=100)  # Keeping for backward compatibility
    variation = models.CharField(max_length=100)  # Keeping for backward compatibility
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_quantity = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True)
    is_default = models.BooleanField(default=False)
    
    
    # Change these foreign keys to ManyToMany relationships
    sizes = models.ManyToManyField(Size, related_name='variations', blank=True)
    colors = models.ManyToManyField(Color, related_name='variations', blank=True)
    
    # Keep these for backward compatibility
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True, related_name='single_variations')
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, related_name='single_variations')

    class Meta:
        unique_together = ['product', 'variation_type', 'variation']

    def __str__(self):
        return f"{self.product.name} - {self.variation_type}: {self.variation}"

class ProductSize(models.Model):
    product = models.ForeignKey(Product, related_name='available_sizes', on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['product', 'size']
    
    def __str__(self):
        return f"{self.product.name} - Size: {self.size.name}"

class ProductColor(models.Model):
    product = models.ForeignKey(Product, related_name='available_colors', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['product', 'color']
    
    def __str__(self):
        return f"{self.product.name} - Color: {self.color.name}"    

class CarouselItem(models.Model):
    """Model for homepage carousel items/banners"""
    text = models.CharField(max_length=200)  # This will store the ad text
    image = CloudinaryField('image', folder='carousel/')  # This stays the same
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Determines the display order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Carousel Banner"
        verbose_name_plural = "Carousel Banners"

    def __str__(self):
        return self.text
        
class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
        null=True,
        blank=True
    )
    session_key = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'session_key'],
                name='unique_user_session'
            )
        ]
        
    def __str__(self):
        return f"Cart {self.id} - User: {self.user.email if self.user else 'Anonymous'}"
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # Add these new fields:
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        # Update the unique constraint to include size and color
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product', 'size', 'color'],
                name='unique_product_variant_in_cart'
            ),
        ]

    def __str__(self):
        size_info = f", Size: {self.size.name}" if self.size else ""
        color_info = f", Color: {self.color.name}" if self.color else ""
        return f"{self.quantity} x {self.product.name}{size_info}{color_info} in {self.cart}"
        
class Customer(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('blocked', 'Blocked'),
    ]
    
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    country_code = models.CharField(max_length=5, blank=True, null=True) # e.g. +234
    local_phone_number = models.CharField(max_length=20, blank=True, null=True) # The number without country code
    phone = models.CharField(max_length=30, blank=True) # Stores the fully formatted number
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')  # ADD THIS
    photo = CloudinaryField('image', folder='customers/', null=True, blank=True)  # Customer profile photo using Cloudinary
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.country_code and self.local_phone_number:
            # Import here to avoid circular dependency if utils imports models
            from .utils import format_phone_number
            self.phone = format_phone_number(self.country_code, self.local_phone_number)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('CASH', 'Cash'),
        ('CREDIT', 'Credit Card'),
        ('DEBIT', 'Debit Card'),
        ('TRANSFER', 'Bank Transfer'),
        ('CLOVER_HOSTED', 'Clover Hosted'),  # Add this for Clover payments
    ]
    
    ORDER_TYPE_CHOICES = [
        ('STANDARD', 'Standard'),
        ('EXPRESS', 'Express'),
        ('PICKUP', 'Pickup'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('RETURNED', 'Returned'),
        ('DAMAGED', 'Damaged'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    # Customer Information
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    
    # Order Details
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='STANDARD')
    order_date = models.DateField(auto_now_add=True)
    order_time = models.TimeField(auto_now_add=True)
    note = models.TextField(blank=True)
    
    # Payment Information
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')  # KEEP ONLY ONE!
    billing_address = models.TextField(null=True, blank=True)
    
    # Financial Details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Shipping Information
    shipping_address = models.TextField(null=True, blank=True)
    shipping_city = models.CharField(max_length=100, null=True, blank=True)
    shipping_state = models.CharField(max_length=100, null=True, blank=True)
    shipping_country = models.CharField(max_length=100, null=True, blank=True)
    shipping_zip = models.CharField(max_length=20, null=True, blank=True)
    
    # Clover Integration
    clover_session_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number: ORD-YYYYMMDD-XXXX
            last_order = Order.objects.order_by('-id').first()
            if last_order:
                last_id = last_order.id
            else:
                last_id = 0
            self.order_number = f"ORD-{timezone.now().strftime('%Y%m%d')}-{str(last_id + 1).zfill(4)}"
        
        # Calculate total
        self.total = (
            self.subtotal +
            self.shipping_cost +
            self.tax -
            self.discount
        )
        super().save(*args, **kwargs)
    
    def __str__(self):
        if self.customer:
            return f"Order {self.order_number} - {self.customer.name}"
        else:
            return f"Order {self.order_number}"
    
    class Meta:
        ordering = ['-created_at']



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)
        
        # Update order subtotal
        order_items = self.order.items.all()
        self.order.subtotal = sum(item.subtotal for item in order_items)
        self.order.save()

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order {self.order.order_number}"


class OrderTracking(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking_history')
    status = models.CharField(max_length=50)
    location = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Tracking for {self.order.order_number} - {self.status}"

# Wishlist Model
class Wishlist(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, through='WishlistItem')

# WishlistItem Model 
class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

class WishlistNotification(models.Model):
    """Model to store wishlist item stock notifications"""
    wishlist_item = models.ForeignKey(WishlistItem, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

# ProductRecommendation Model
class ProductRecommendation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='recommendations')
    recommended_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='recommended_by')
    score = models.FloatField()

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class ReviewTag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    title = models.CharField(max_length=255)  # New field for review title
    content = models.TextField()  # For review details
    tags = models.ManyToManyField('ReviewTag', related_name='reviews', blank=True)
    variant = models.CharField(max_length=255, blank=True)
    helpful_votes = models.IntegerField(default=0)
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review by {self.user.email} for product #{self.product_id}"

class ReviewHelpfulVote(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes_users')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('review', 'user')
        
    def __str__(self):
        return f"Vote by {self.user.email} for review #{self.review_id}"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
        ('CANCELLED', 'Cancelled')
    ]

    PAYMENT_METHOD_CHOICES = [
        ('VISA', 'Visa'),
        ('MASTERCARD', 'Mastercard'),
        ('PAYPAL', 'PayPal'),
        ('GOOGLE_PAY', 'Google Pay'),
        ('STRIPE', 'Stripe'),
        ('CLOVER', 'Clover'),
        ('CLOVER_HOSTED', 'Clover Hosted Checkout')
    ]

    card_last_four = models.CharField(max_length=4, null=True, blank=True)
    card_brand = models.CharField(max_length=20, null=True, blank=True)
    card_expiry = models.CharField(max_length=7, null=True, blank=True)  # Format: MM/YYYY
    save_card = models.BooleanField(default=False)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    gateway_response = models.JSONField(null=True, blank=True)
    method = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Payment {self.transaction_id} for Order {self.order.id}"
    
    clover_checkout_session_id = models.CharField(max_length=255, null=True, blank=True, help_text="Clover hosted checkout session ID")
    clover_checkout_url = models.URLField(null=True, blank=True, help_text="Clover hosted checkout URL")
    clover_payment_id = models.CharField(max_length=255, null=True, blank=True, help_text="Clover payment ID after completion")

    def __str__(self):
        return f"Payment {self.transaction_id} for Order {self.order.id}"
    
    class Meta:
        ordering = ['-created_at']


class SavedPaymentMethod(models.Model):
    PAYMENT_TYPES = (
        ('STRIPE', 'Stripe'),
        ('PAYPAL', 'PayPal'),
        ('CLOVER', 'Clover'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    token = models.CharField(max_length=255)
    card_last_four = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'token')

class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, default="")
    email = models.EmailField(max_length=255, default="")
    phone_number = models.CharField(max_length=20, default="")
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def save(self, *args, **kwargs):
        if self.is_default:
            # Set all other addresses of user to non-default
            Address.objects.filter(user=self.user).update(is_default=False)
        super().save(*args, **kwargs)

class ShippingMethod(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} (${self.price})"

class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    minimum_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def is_valid(self, total_amount):
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            total_amount >= self.minimum_purchase
        )

class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed')
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='support_tickets', null=True, blank=True)
    full_name = models.CharField(max_length=255)  # New field to match UI
    message = models.TextField()  # This matches the "Complaint" field in UI
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Help Request #{self.id} - {self.full_name}"
    
class TicketResponse(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    is_staff_response = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='ticket_attachments/', null=True, blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Response to ticket #{self.ticket.id}"
    
    
