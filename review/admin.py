from django.contrib import admin
from .models import Review, ReviewStatus


@admin.action(description="Approve selected reviews")
def approve_reviews(modeladmin, request, queryset):
    queryset.update(status=ReviewStatus.APPROVED)
    

@admin.action(description="Reject selected reviews")
def reject_reviews(modeladmin, request, queryset):
    queryset.update(status=ReviewStatus.REJECTED)


# Register your models here.
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "comment", "status", "created_at", "updated_at")
    list_filter = ("product", "rating", "status")
    actions = [approve_reviews, reject_reviews]
    search_fields = ("product__name", "user__firstname")
    readonly_fields = ("product", "user", "created_at", "updated_at")
