import uuid
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.conf import settings

from catalog.models import Product

User = settings.AUTH_USER_MODEL

# Cart Status Enum
class CartStatus(models.TextChoices):
    ACTIVE = "active", "ACTIVE"
    CHECKED_OUT = "checked_out", "CHECKED_OUT"
    EXPIRED = "expired", "EXPIRED"


# Create your models here.
class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    status = models.CharField(max_length=15, choices=CartStatus.choices, default=CartStatus.ACTIVE)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    TTL = timedelta(days=15)
    EXTENSION = timedelta(hours=12)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"], condition=models.Q(status="ACTIVE"),
                name="unique_active_cart_per_user"
            )
        ]
        
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timedelta.now + self.TTL
        super().save(*args, **kwargs)
        
    def extend_ttl(self):
        """ Extends cart expiration when the user interacts meaningfully """
        self.expires_at = max(self.expires_at, timedelta.now() + self.EXTENSION)
        self.save()
    
    def __str__(self):
        return f"Cart: {self.id}, Status: {self.status}"
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_item")
    quantity = models.PositiveIntegerField(default=1)
    price_snapshot = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"CartItem: {self.id}, Quantity: {self.quantity}"
