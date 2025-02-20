from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from cloudinary.forms import CloudinaryFileField
from django import forms
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
    TicketResponse
)

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
    
# Support Ticket Admin
admin.site.register(SupportTicket)
admin.site.register(TicketResponse)

# Custom User Admin
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

# Product Variation Inline (keeping your existing inline)
class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1

# Updated Product Admin Form
class ProductAdminForm(forms.ModelForm):
    main_image = CloudinaryFileField(
        options = {
            'folder': 'products/',
            'allowed_formats': ['jpg', 'png'],
            'crop': 'limit',
            'width': 1000,
            'height': 1000,
        },
        required=False
    )
    
    image_uploads = MultipleFileField(
        required=False,
        label='Additional Images'
    )
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
# Updated Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    inlines = [ProductVariationInline]
    
    def image_preview(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" width="50" height="50" style="margin-right: 5px;" />', obj.main_image.url)
        return "No main image"
    image_preview.short_description = 'Main Image'
    
    def display_additional_images(self, obj):
        if not obj.images:
            return "No additional images"
        
        html = []
        for img_url in obj.images[:3]:  # Show first 3 images
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
            'description': 'Upload product images. Main image will be displayed as the primary product image. Use image_uploads for additional product images.'
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
        ('Product Details', {
            'fields': (
                'is_featured',
                'is_physical_product',
                'weight',
                'height',
                'length',
                'width'
            )
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
        files = request.FILES.getlist('image_uploads')
        if files:
            from cloudinary.uploader import upload
            uploaded_urls = []
            
            for file in files:
                result = upload(
                    file,
                    folder='products/',
                    resource_type='auto'
                )
                uploaded_urls.append(result['secure_url'])
            
            # Update the images JSON field
            current_images = obj.images or []
            obj.images = current_images + uploaded_urls
        
        if not obj.slug:
            from django.utils.text import slugify
            obj.slug = slugify(obj.name)
        
        super().save_model(request, obj, form, change)
# Other model registrations
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

# Register CustomUser
admin.site.register(CustomUser, CustomUserAdmin)