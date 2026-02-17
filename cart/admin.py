from django.contrib import admin, messages
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
    
    actions = ['mark_selected_carts_expired', 'extend_selected_carts']
    
    # Mark selected carts as expired
    def mark_selected_carts_expired(self, request, queryset):
        success_count = 0
        for cart in queryset:
            try:
                cart.mark_expired()
                cart.save()
                success_count += 1
            except  Exception as e:
                self.message_user(request, f"Error expiring cart {cart.id}: {e}", level=messages.ERROR)
        self.message_user(request, f"{success_count} cart(s) successfully marked as expired.")


    mark_selected_carts_expired.short_description = "Mark selected carts as expired"


    # Extend expiration by X minutes (example: 30)
    def extend_selected_carts(self, request, queryset):
        ttl_minutes = 30
        success_count = 0
        for cart in queryset:
            try:
                cart.extend_expiration(ttl_minutes)
                cart.save()
                success_count += 1
            except Exception as e:
                self.message_user(request, f"Error extending cart {cart.id}: {e}", level=messages.ERROR)
        self.message_user(request, f"{success_count} cart(s) extended by {ttl_minutes} minutes.")

    extend_selected_carts.short_description = "Extend selected carts expiration by 30 minutes"
   
    
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'price_snapshot', 'reservation', 'created_at')
    list_filter = ('cart__status', 'product')
    search_fields = ('cart__id', 'product__name')
    readonly_fields = ('cart', 'product', 'quantity', 'price_snapshot', 'reservation', 'created_at')
    can_delete = False
    
