from django.contrib import admin
from .models import Cart, CartItem

# Inline display for CartItem with Cart
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price_snapshot', 'reservation')
    can_delete = False


# Register your models here.
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'expires_at', 'created_at', 'updated_at')
    list_filter = ('status', 'user')
    search_fields = ('id', 'user__first_name', 'user__email')
    readonly_fields = ('id', 'created_at', 'updated_at', 'expires_at', 'status')
    inlines = [CartItemInline]
   
    
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'price_snapshot', 'reservation', 'created_at')
    list_filter = ('cart__status', 'product')
    search_fields = ('cart__id', 'product__name')
    readonly_fields = ('cart', 'product', 'quantity', 'price_snapshot', 'reservation', 'created_at')
    can_delete = False
    
