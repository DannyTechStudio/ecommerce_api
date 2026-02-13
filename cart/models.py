import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

from catalog.models import Product
from inventory.models import InventoryReservation

User = settings.AUTH_USER_MODEL


class CartStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    CHECKED_OUT = "CHECKED_OUT", "Checked_out"
    EXPIRED = "EXPIRED", "Expired"


# Create your models here.
class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    status = models.CharField(max_length=15, choices=CartStatus.choices, default=CartStatus.ACTIVE)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    # Checking for the usability of a cart
    def is_active(self) -> bool:
        if self.status == CartStatus.ACTIVE:
            return False
        
        if self.expires_at is None:
            return False
        
        return timezone.now() < self.expires_at
    
    
    # Extends cart expiration duration
    def extend_expiration(self, ttl_minutes: int) -> None:
        if self.status != CartStatus.ACTIVE:
            raise ValueError("Only active carts can be extended")
        
        if ttl_minutes <= 0:
            raise ValueError("Cart time to live must be positive")
        
        self.expires_at = timezone.now() + timezone.timedelta(minutes=ttl_minutes)
        
        
    # Marks a cart as checked out
    def mark_checked_out(self) -> None:
        if self.status != CartStatus.ACTIVE:
            raise ValueError("Only active carts can be checked out")
        
        self.status = CartStatus.CHECKED_OUT
        self.expires_at = None
        
        
    # Marks a cart as expired
    def mark_expired(self) -> None:
        if self.status == CartStatus.CHECKED_OUT:
            raise ValueError("Checked out carts cannot expire")
        
        self.status = CartStatus.EXPIRED
        self.expires_at = None
    
    
    
    
        
