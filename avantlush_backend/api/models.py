from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
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

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-created_at']

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state}"

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
    tags = models.ManyToManyField('Tag', blank=True)
    categories = models.ManyToManyField('Category', blank=True, related_name='secondary_products')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Order #{self.id} by {self.user.email}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"

# Wishlist Model
class Wishlist(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, through='WishlistItem')

# WishlistItem Model 
class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

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