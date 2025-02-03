from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import Order, OrderItem
from django.contrib import admin
from .models import SupportTicket, TicketResponse
from .models import (
    WaitlistEntry,
    CustomUser,
    PasswordResetToken,
    EmailVerificationToken,
    Product,
    Article,
    Cart,
    CartItem,
    Order,
    Profile,
    Address
)

admin.site.register(SupportTicket)
admin.site.register(TicketResponse)

# CustomUser Admin
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

# WaitlistEntry Admin
@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(admin.ModelAdmin):
    list_display = ('email', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('email',)
    ordering = ('-timestamp',)

# Token Admins
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

# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    def product_category(self, obj):
        return obj.category.name if obj.category else '-'
    product_category.short_description = 'Category'

    list_display = ('name', 'price', 'product_category', 'stock_quantity', 'status', 'is_featured')
    list_filter = ('status', 'is_featured', 'category')
    search_fields = ('name', 'description', 'sku')
# Article Admin
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)

# Cart Admin
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__email',)
    ordering = ('-created_at',)

# CartItem Admin
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    search_fields = ('cart__user__email', 'product__name')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at', 'payment_status')
    search_fields = ('user__email', 'shipping_address')
    ordering = ('-created_at',)
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'status', 'payment_status')
        }),
        ('Shipping Information', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_state', 
                      'shipping_country', 'shipping_zip')
        }),
        ('Payment Information', {
            'fields': ('subtotal', 'shipping_cost', 'discount', 'total', 'payment_method')
        }),
    )
# Profile Admin
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__email', 'phone_number')

# Address Admin
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'street_address', 'city', 'state', 'is_default')
    list_filter = ('is_default', 'state')
    search_fields = ('user__email', 'street_address', 'city', 'state')

# Register CustomUser
admin.site.register(CustomUser, CustomUserAdmin)
