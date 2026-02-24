from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        'product_id',
        'product_name',
        'quantity',
        'unit_price',
        'line_total',
    )
    can_delete = False


# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user", "status", "total_price", "created_at",)
    list_filter = ["status", "created_at",]
    search_fields = ["order_number", "user__email"]
    ordering = ["-created_at"]
    readonly_fields = [field.name for field in Order._meta.fields]
    inlines = [OrderItemInline]
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product_id", "product_name", "quantity", "unit_price", "line_total")
    list_filter = ["order__status"]
    search_fields = ["product_name"]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request):
        return False