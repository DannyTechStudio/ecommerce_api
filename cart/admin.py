from django.contrib import admin
from .models import Cart, CartItem


# Register your models here.
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("product", "quantity", "price_snapshot")
    can_delete = False
    
    
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at", "expires_at")
    list_filter = ["status", "created_at"]
    search_fields = ["user__email", "user__id"]
    ordering = ["-created_at"]
    inlines = [CartItemInline]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "quantity", "price_snapshot")
    list_filter = ["cart__status"]
    search_fields = ["product__name"]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request):
        return False