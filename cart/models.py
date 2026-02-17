import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Q

from catalog.models import Product
from inventory.models import InventoryReservation

User = settings.AUTH_USER_MODEL


# Cart Status Enum
class CartStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    CHECKED_OUT = "CHECKED_OUT", "Checked_out"
    EXPIRED = "EXPIRED", "Expired"


# Create your models here.
class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    status = models.CharField(max_length=15, choices=CartStatus.choices, default=CartStatus.ACTIVE)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(status=CartStatus.ACTIVE),
                name="one_active_cart_per_user"
            )  
        ]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["expires_at"]),
        ]
    
    def __str__(self):
        return f"Cart: {self.id} Owner: {self.user} Status: {self.status}" 


    # Checking for the usability of a cart
    def is_active(self):
        if self.status != CartStatus.ACTIVE:
            return False
        
        if self.expires_at is None:
            return False
        
        return timezone.now() < self.expires_at
    

    # Extends cart expiration duration
    def extend_expiration(self, ttl_minutes):
        if self.status != CartStatus.ACTIVE:
            raise ValueError("Only active carts can be extended")
        
        if ttl_minutes <= 0:
            raise ValueError("Cart time to live must be positive")
        
        self.expires_at = timezone.now() + timezone.timedelta(minutes=ttl_minutes)
        
        
    # Marks a cart as checked out
    def mark_checked_out(self):
        if self.status != CartStatus.ACTIVE:
            raise ValueError("Only active carts can be checked out")
        
        self.status = CartStatus.CHECKED_OUT
        self.expires_at = None
        
        
    # Marks a cart as expired
    def mark_expired(self):
        if self.status == CartStatus.CHECKED_OUT:
            raise ValueError("Checked out carts cannot expire")
        
        self.status = CartStatus.EXPIRED
        self.expires_at = None


# CartItem Model Class
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField()
    reservation = models.ForeignKey(InventoryReservation, on_delete=models.PROTECT, related_name="cart_items")
    price_snapshot = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="unique_product_per_cart"
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="quantity_must_be_positive"
            )
        ]
    
    def __str__(self):
        return f"Item: {self.id} Cart: {self.cart} Product: {self.product} Reservation: {self.reservation}"
    
    # Increase cart item quantity
    def increase_quantity(self, amount):
        if amount <= 0:
            raise ValueError("Increase amount must be positive")
        
        self.quantity += amount
     
        
    # Decrease cart item quantity
    def decrease_quantity(self, amount):
        if amount <= 0:
            raise ValueError("Decrease amount must be positive")
        
        if amount > self.quantity:
            raise ValueError("Cannot reduce below zero")
        
        self.quantity -= amount
        
    
    # Locking price at the time of adding to cart
    def update_price_snapshot(self, price):
        if price < 0:
            raise ValueError("Price cannot be negative")
        
        self.price_snapshot = price
        
    
    # Adding reservation
    def attach_reservation(self, reservation_id):
        if not reservation_id:
            raise ValueError("Reservation ID is required")
        
        self.reservation = reservation_id
