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
    ProductVariantImage,
)

# Product Forms
class ProductAdminForm(forms.ModelForm):
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

    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
from django.forms.widgets import ClearableFileInput
class ProductVariationForm(forms.ModelForm):
    variant_images = CloudinaryFileField(
        options={
            'folder': 'product_variants/',
            'allowed_formats': ['jpg', 'png'],
            'crop': 'limit',
            'width': 1000,
            'height': 1000,
        },
        required=False
    )
    
    class Meta:
        model = ProductVariation
        fields = ['variation_type', 'variation', 'price_adjustment', 
                 'stock_quantity', 'sku', 'is_default']

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
class ProductVariantImageInline(admin.TabularInline):
    model = ProductVariantImage
    extra = 1
    fields = ('image', 'is_primary')

class ProductVariationInline(admin.StackedInline):
    model = ProductVariation
    form = ProductVariationForm
    extra = 1
    fields = (
        ('variation_type', 'variation'),
        ('price_adjustment', 'stock_quantity'),
        ('sku', 'is_default'),
        'variant_image',
    )

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['variant_image'].widget = forms.ClearableFileInput()
        return formset

    def display_images(self, obj):
        if not obj.pk:
            return "Save to view image"
            
        image = ProductVariantImage.objects.filter(variant=obj, is_primary=True).first()
        if not image:
            return "No image"
            
        return format_html('<img src="{}" width="50" height="50" />', image.image.url)
    display_images.short_description = 'Current Image'

# Admin Classes
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
        files = request.FILES.getlist('variant_images')
        if files:
            from cloudinary.uploader import upload
            
            # Get or create default variant if none exists
            default_variant, created = ProductVariation.objects.get_or_create(
                product=obj,
                variation_type='default',
                variation='default',
                defaults={'is_default': True}
            )
            
            for file in files:
                result = upload(
                    file,
                    folder=f'products/variants/{obj.id}/',
                    resource_type='auto'
                )
                ProductVariantImage.objects.create(
                    variant=default_variant,
                    image=result['secure_url']
                )
        
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        
        for instance in instances:
            instance.save()
            
            if isinstance(instance, ProductVariation):
                form_index = next((i for i, f in enumerate(formset.forms) 
                                if f.instance == instance), None)
                if form_index is not None:
                    form = formset.forms[form_index]
                    image_file = form.cleaned_data.get('variant_image')
                    
                    if image_file:
                        from cloudinary.uploader import upload
                        try:
                            # Delete existing primary image if any
                            ProductVariantImage.objects.filter(
                                variant=instance, 
                                is_primary=True
                            ).delete()
                            
                            # Upload new image
                            result = upload(
                                image_file,
                                folder=f'product_variants/{instance.product.id}/{instance.id}/',
                                resource_type='auto'
                            )
                            
                            # Create new primary image
                            ProductVariantImage.objects.create(
                                variant=instance,
                                image=result['secure_url'],
                                is_primary=True
                            )
                        except Exception as e:
                            messages.error(request, f"Failed to upload image: {str(e)}")
        
        formset.save_m2m()
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

@admin.register(ProductVariantImage)
class ProductVariantImageAdmin(admin.ModelAdmin):
    list_display = ['variant', 'image', 'is_primary']
    list_filter = ['is_primary', 'variant']

# Final registrations
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SupportTicket)
admin.site.register(TicketResponse)