from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

import uuid

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
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='primary_products')
    name = models.CharField(max_length=255)
    description = models.TextField()
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

    main_image = models.ImageField(
    upload_to='products/main/',
    null=True,
    blank=True
)
    # New fields for detailed product management
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name='products')
    tags = models.ManyToManyField('Tag', blank=True)
    
    # Pricing fields
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_type = models.CharField(max_length=20, choices=[
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
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

class ProductVariation(models.Model):
    product = models.ForeignKey(
        Product, 
        related_name='variations', 
        on_delete=models.CASCADE
    )
    variation_type = models.CharField(max_length=100)
    variation = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.product.name} - {self.variation_type}: {self.variation}"
    
class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.email}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Existing fields
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # New fields for checkout
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_country = models.CharField(max_length=100)
    shipping_zip = models.CharField(max_length=20)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, null=True)
    payment_status = models.CharField(max_length=50, default='PENDING')

    def __str__(self):
        return f"Order #{self.id} by {self.user.email}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total(self):
        return self.quantity * self.price
        
class OrderTracking(models.Model):
    """Model to store detailed order tracking history"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking_history')
    status = models.CharField(max_length=50)
    location = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']


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
    """Model for predefined review tags like 'Fast shipping', 'Good quality', etc."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    content = models.TextField()
    images = models.JSONField(default=list)  # Store list of image URLs
    tags = models.ManyToManyField(ReviewTag, related_name='reviews')
    helpful_votes = models.PositiveIntegerField(default=0)
    variant = models.CharField(max_length=100, blank=True)  # Store variant info like "White"
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        # Ensure one review per user per product
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_user_product_review'
            )
        ]

    def save(self, *args, **kwargs):
        # Update product rating on save
        super().save(*args, **kwargs)
        self.update_product_rating()

    def update_product_rating(self):
        product = self.product
        reviews = product.reviews.all()
        if reviews:
            avg_rating = sum(review.rating for review in reviews) / len(reviews)
            product.rating = round(avg_rating, 2)
            product.num_ratings = len(reviews)
            product.save()

class ReviewHelpfulVote(models.Model):
    """Track who has voted a review as helpful"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure one vote per user per review
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'review'],
                name='unique_user_review_vote'
            )
        ]

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded')
    ]

    PAYMENT_METHOD_CHOICES = [
        ('VISA', 'Visa'),
        ('MASTERCARD', 'Mastercard'),
        ('PAYPAL', 'PayPal'),
        ('GOOGLE_PAY', 'Google Pay'),
        ('STRIPE', 'Stripe')
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
    
class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
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
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='OPEN')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"

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