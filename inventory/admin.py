from django.contrib import admin
from .models import (
    InventoryItem,
    InventoryReservation,
    InventoryMovement
)

# Register your models here.
@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "quantity_on_hand",
        "quantity_reserved",
        "available_quantity",
        "created_at",
    )
    
    search_fields = ("product__name",)
    readonly_fields = ("quantity_reserved", "created_at")
    
    
@admin.register(InventoryReservation)
class InventoryReservationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "inventory_item",
        "customer",
        "quantity",
        "is_active",
        "created_at",
        "expires-at",
    )
    
    list_filter = ("is_active", "created_at", "expires_at")
    search_fields = ("customer__email")
    readonly_fields = ("created_at")
    
    
@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "inventory_item",
        "quantity",
        "movement_type",
        "reference",
        "created_at",
    )
    
    list_filter = ("movement_type", "created_at")
    readonly_fields = ("created_at")