from django.contrib import admin
from .models import PaymentMethod, Payment, PaymentEvent

# Register your models here.
@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "provider", "channel", "code", "is_active", "supports_refund", "created_at")
    list_filter = ("is_active", "supports_refund")
    search_fields = ("name", "code")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("reference", "order", "amount", "currency", "status", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("reference", "provider_reference")
    readonly_fields = ("reference", "provider_reference", "provider_response", "created_at", "paid_at")


@admin.register(PaymentEvent)
class PaymentEventAdmin(admin.ModelAdmin):
    list_display = ("payment", "event_type", "created_at",)
    search_fields = ("payment__reference", "event_type",)
    readonly_fields = ("payment", "event_type", "payload", "created_at",)
