import uuid
from django.db import models

from order.models import Order


# Payment Status Enum
class PaymentStatus(models.TextChoices):
    INITIATED = "initiated", "Initiated"
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    SUCCESS = 'success', 'Success'
    FAILED = 'failed', 'Failed'
    REFUNDED = 'refunded', 'Refunded'
    
    
# Payment Provider Enum
class ProviderChoices(models.TextChoices):
    PAYSTACK = "paystack", "Paystack"
    
    
# Payment Channel Enum
class ChannelChoices(models.TextChoices):
    CARD = "card", "Card"
    MOMO = "momo", "Momo"
    BANK = "bank", "Bank"


# Create your models here.
class PaymentMethod(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=50, choices=ProviderChoices.choices)
    channel = models.CharField(max_length=50, choices=ChannelChoices.choices)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True)
    supports_refund = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    
class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="GHS")
    reference  = models.CharField(max_length=255, unique=True)
    provider_reference = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=15, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    provider_response = models.JSONField(default=dict, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "channel"],
                name="unique_provider_channel"
            )
        ]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=["reference"]),
            models.Index(fields=["provider_reference"]),
            models.Index(fields=['order', 'status']),
        ]
        
    
    def __str__(self):
        return f"{self.order.order_number} - {self.method}"
    
    
# Payment Event Model
class PaymentEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="events", null=True, blank=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
