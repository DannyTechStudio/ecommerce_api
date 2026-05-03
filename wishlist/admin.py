from django.contrib import admin
from .models import WishList, WishListItem


# Register your models here.
class WishListItemInline(admin.TabularInline):
    model = WishListItem
    extra = 0
    can_delete = False
    readonly_fields = ("product", "added_at")
    show_change_link = True


@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    search_fields = ("user__email", "user__full_name")
    readonly_fields = ("created_at",)
    inlines = [WishListItemInline]
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "items"
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(WishListItem)
class WishListItemAdmin(admin.ModelAdmin):
    list_display = ("id", "wishlist", "product", "added_at")
    search_fields = ("product__name", "wishlist__user__email", "wishlist__user__full_name")
    list_filter = ("added_at",)
    readonly_fields = ("wishlist", "product", "added_at")
    
    def user(self, obj):
        return obj.wishlist.user
    user.short_description = "User"

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False