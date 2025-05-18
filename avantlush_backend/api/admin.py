from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from cloudinary.forms import CloudinaryFileField
from cloudinary.models import CloudinaryField
from django import forms
from django.db import models
from django.forms import FileInput
from .models import (
    WaitlistEntry,
    CustomUser,
    PasswordResetToken,
    EmailVerificationToken,
    Product,
    ProductVariation,
    Article,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Profile,
    Address,
    OrderTracking,
    SupportTicket,
    TicketResponse,
    Category,
    CarouselItem,
    Size,
    Color,
    ProductSize,
    ProductColor,
)

# Product Forms
class ProductAdminForm(forms.ModelForm):
    product_details_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6}),
        required=False,
        help_text="Enter product details, one per line. Each line will be displayed as a bullet point."
    )
    
    main_image = CloudinaryFileField(
        options={
            'folder': 'products/',
            'allowed_formats': ['jpg', 'png'],
            'crop': 'limit',
            'width': 1000,
            'height': 1000,
        },
        required=False
    )
    
    image_uploads = CloudinaryFileField(
        options={
            'folder': 'products/',
            'allowed_formats': ['jpg', 'png'],
            'crop': 'limit',
            'width': 1000,
            'height': 1000,
        },
        required=False,
        label="Additional Images",
        help_text="Upload additional product images"
    )

    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide the original JSON field
        if 'product_details' in self.fields:
            self.fields['product_details'].widget = forms.HiddenInput()
        
        # If we're editing an existing product, populate the text field
        if self.instance.pk and hasattr(self.instance, 'product_details') and self.instance.product_details:
            self.fields['product_details_text'].initial = '\n'.join(self.instance.product_details)
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Handle product details text conversion
        details_text = cleaned_data.get('product_details_text', '')
        if details_text:
            # Split by new lines and remove empty lines
            details_list = [line.strip() for line in details_text.split('\n') if line.strip()]
            cleaned_data['product_details'] = details_list
        else:
            cleaned_data['product_details'] = []
        
        # Handle the image uploads and append them to the images JSON field
        image_upload = cleaned_data.get('image_uploads')
        if image_upload:
            instance = self.instance
            current_images = instance.images if instance.pk and instance.images else []
            
            # Store the Cloudinary URL in the images array
            current_images.append(image_upload.url)
            cleaned_data['images'] = current_images
        
        return cleaned_data

from django.forms.widgets import ClearableFileInput
class ProductVariationForm(forms.ModelForm):
    
    class Meta:
        model = ProductVariation
        fields = ['variation_type', 'variation', 'price_adjustment', 
                 'stock_quantity', 'sku', 'is_default', 
                 # Old single fields (for backward compatibility)
                 'size', 'color',
                 # New many-to-many fields
                 'sizes', 'colors']
# Filters
class StockFilter(SimpleListFilter):
    title = 'stock status'
    parameter_name = 'stock_status'
    
    def lookups(self, request, model_admin):
        return (
            ('out', 'Out of Stock'),
            ('low', 'Low Stock (<10)'),
            ('in', 'In Stock'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'out':
            return queryset.filter(stock_quantity=0)
        if self.value() == 'low':
            return queryset.filter(stock_quantity__gt=0, stock_quantity__lt=10)
        if self.value() == 'in':
            return queryset.filter(stock_quantity__gte=10)

# Inlines

class ProductVariationInline(admin.StackedInline):
    model = ProductVariation
    form = ProductVariationForm
    extra = 1
    fields = (
        ('variation_type', 'variation'),
        # Old single fields (for backward compatibility)
        ('size', 'color'),
        # New many-to-many fields
        ('sizes', 'colors'),
        ('price_adjustment', 'stock_quantity'),
        ('sku', 'is_default'),
        
    )

    

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1

# Admin Classes
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    inlines = [ProductVariationInline, ProductColorInline, ProductVariationInline]
    
    def image_preview(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" width="50" height="50" style="margin-right: 5px;" />', obj.main_image.url)
        return "No main image"
    image_preview.short_description = 'Main Image'
    
    def display_additional_images(self, obj):
        if not obj.images:
            return "No additional images"
        
        html = []
        for img_url in obj.images[:3]:
            html.append(f'<img src="{img_url}" width="50" height="50" style="margin-right: 5px;" />')
        
        if len(obj.images) > 3:
            html.append(f'<span>+{len(obj.images) - 3} more</span>')
            
        return format_html(''.join(html))
    display_additional_images.short_description = 'Additional Images'
    
    def product_category(self, obj):
        return obj.category.name if obj.category else '-'
    product_category.short_description = 'Category'
    
    list_display = (
        'image_preview',
        'display_additional_images',
        'name',
        'sku',
        'price',
        'product_category',
        'stock_quantity',
        'status',
        'is_featured'
    )
    
    list_filter = (
        StockFilter,
        'status',
        'is_featured',
        'category',
        'created_at'
    )
    
    search_fields = (
        'name',
        'description',
        'sku',
        'category__name'
    )
    
    readonly_fields = (
        'created_at',
        'updated_at',
        'rating',
        'num_ratings'
    )
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'description',
                'sku',
                'slug',
                'category',
                'tags'
            )
        }),
        ('Images', {
            'fields': (
                'main_image',
                'image_uploads',
                'images',
            ),
            'description': 'Upload product images. Main image will be displayed as the primary product image.'
        }),
        ('Pricing', {
            'fields': (
                'price',
                'base_price',
                'discount_type',
                'discount_percentage',
                'vat_amount'
            )
        }),
        ('Inventory', {
            'fields': (
                'stock_quantity',
                'status',
                'barcode'
            )
        }),
        ('Available Variations', {
            'fields': [],
            'description': 'Product variations are managed in the sections below. Add available sizes and colors, then create specific variations.'
        }),
        ('Product Details', {
            'fields': (
                'product_details_text', 
                'is_featured',
                'is_physical_product',
                'weight',
                'height',
                'length',
                'width'
            ),
            'description': 'Enter product details as a list of features. Each item will be displayed as a bullet point.'
        }),
        ('Metrics', {
            'fields': (
                'rating',
                'num_ratings',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    list_per_page = 20
    save_on_top = True
    
    def save_model(self, request, obj, form, change):
        # Explicitly set product_details from the form's cleaned data
        if 'product_details' in form.cleaned_data:
            obj.product_details = form.cleaned_data['product_details']
            
        
        admin.ModelAdmin.save_model(self, request, obj, form, change)
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        
        for instance in instances:
            instance.save()
            
# Other Admin Registrations
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'location', 'is_active', 'date_joined', 'is_staff')
    search_fields = ('email', 'location')
    ordering = ('-date_joined',)
    list_filter = ('is_active', 'is_staff', 'location')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'location'),
        }),
    )
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('location',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(admin.ModelAdmin):
    list_display = ('email', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('email',)
    ordering = ('-timestamp',)

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'is_used')
    search_fields = ('user__email',)
    list_filter = ('is_used', 'created_at')

@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'is_used')
    search_fields = ('user__email',)
    list_filter = ('is_used', 'created_at')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    list_filter = ('parent',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(CarouselItem)
class CarouselItemAdmin(admin.ModelAdmin):
    list_display = ('text', 'order', 'active', 'created_at')
    list_filter = ('active',)
    search_fields = ('text',)
    ordering = ('order',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Content', {
            'fields': ('text',)
        }),
        ('Image', {
            'fields': ('image',)
        }),
        ('Settings', {
            'fields': ('order', 'active', 'created_at', 'updated_at')
        }),
    )
    
@admin.register(ProductVariation)
class ProductVariationAdmin(admin.ModelAdmin):
    form = ProductVariationForm
    filter_horizontal = ('sizes', 'colors')
    list_display = ('product', 'variation_type', 'variation', 'sku')
    search_fields = ('product__name', 'sku')
    
    def save_model(self, request, obj, form, change):
        """Override save_model to sync sizes and colors when a variation is saved"""
        super().save_model(request, obj, form, change)
        # Sync available sizes and colors for the product
        self.sync_product_variations(obj.product)
        
    def save_formset(self, request, form, formset, change):
        """Override save_formset to sync sizes and colors after formset is saved"""
        instances = formset.save()
        
        # If this is a ProductVariation formset, sync the product variations
        if formset.model == ProductVariation and instances:
            for instance in instances:
                self.sync_product_variations(instance.product)
                
    def sync_product_variations(self, product):
        """Sync sizes and colors for a product based on its variations"""
        self.sync_available_sizes(product)
        self.sync_available_colors(product)
        messages.success(request, f"Product '{product.name}' variants synchronized successfully")
    
    def sync_available_sizes(self, product):
        """Synchronize available sizes for the product based on its variations"""
        # Get all sizes from variations
        variation_sizes = set()
        for variation in product.variations.all():
            # Add sizes from ManyToMany relationship
            variation_sizes.update(size.id for size in variation.sizes.all())
            # Add size from ForeignKey relationship if exists
            if variation.size:
                variation_sizes.add(variation.size.id)
        
        # Clear existing product sizes
        ProductSize.objects.filter(product=product).delete()
        
        # Create new product sizes
        for size_id in variation_sizes:
            try:
                size = Size.objects.get(id=size_id)
                ProductSize.objects.create(product=product, size=size)
            except Size.DoesNotExist:
                pass
        
        # Update available_sizes field if you're using it (seems to be a JSONField)
        product.available_sizes = list(variation_sizes)
        # Use update to avoid triggering other save signals
        Product.objects.filter(id=product.id).update(available_sizes=list(variation_sizes))
    
    def sync_available_colors(self, product):
        """Synchronize available colors for the product based on its variations"""
        # Get all colors from variations
        variation_colors = set()
        for variation in product.variations.all():
            # Add colors from ManyToMany relationship
            variation_colors.update(color.id for color in variation.colors.all())
            # Add color from ForeignKey relationship if exists
            if variation.color:
                variation_colors.add(variation.color.id)
        
        # Clear existing product colors
        ProductColor.objects.filter(product=product).delete()
        
        # Create new product colors
        for color_id in variation_colors:
            try:
                color = Color.objects.get(id=color_id)
                ProductColor.objects.create(product=product, color=color)
            except Color.DoesNotExist:
                pass
        
        # Update available_colors field if you're using it (seems to be a JSONField)
        product.available_colors = list(variation_colors)
        # Use update to avoid triggering other save signals
        Product.objects.filter(id=product.id).update(available_colors=list(variation_colors))    

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code', 'color_preview')
    search_fields = ('name',)
    
    def color_preview(self, obj):
        if obj.hex_code:
            return format_html(
                '<div style="background-color: {}; width: 20px; height: 20px; border: 1px solid #ccc;"></div>',
                obj.hex_code
            )
        return "N/A"
    color_preview.short_description = "Color"

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__email',)
    ordering = ('-created_at',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    search_fields = ('cart__user__email', 'product__name')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)

class OrderTrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 0
    readonly_fields = ('timestamp',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__email', 'phone_number')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'street_address', 'city', 'state', 'is_default')
    list_filter = ('is_default', 'state')
    search_fields = ('user__email', 'street_address', 'city', 'state')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__email')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline, OrderTrackingInline]

# Final registrations
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SupportTicket)
admin.site.register(TicketResponse)
