import uuid
from datetime import timezone, timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from catalog.models import Product

User = settings.AUTH_USER_MODEL

# InventoryItem model: product stock tracker
class InventoryItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_items')
    quantity_on_hand = models.PositiveIntegerField()
    quantity_reserved = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Product: {self.product.name}, Stock on Hand: {self.quantity_on_hand}, Reserved: {self.quantity_reserved}"
    
    def available_quantity(self):
        return self.quantity_on_hand - self.quantity_reserved
    
    def reserve_stock(self, quantity):
        if quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        
        if quantity > self.available_quantity():
            raise ValidationError("Insufficient stock available.")
        
        self.quantity_reserved += quantity
        self.save()
        
        InventoryMovement.create(
            inventory_item=self, 
            quantity=quantity, 
            movement_type='RESERVE', 
            reference="cart"
        )
    
    def release_reserved_stock(self, quantity):
        if quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        
        if quantity > self.quantity_reserved:
            raise ValidationError("Cannot release more than reserved.")
        
        self.quantity_reserved -= quantity
        self.save()

        InventoryMovement.create(
            inventory_item=self, 
            quantity=quantity, 
            movement_type='RELEASE', 
            reference="reservation_expired"
        )
    
    def deduct_stock(self, quantity):
        if quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        
        if quantity > self.quantity_reserved:
            raise ValidationError("Cannot deduct more than reserved stock.")
        
        self.quantity_reserved -= quantity
        self.quantity_on_hand -= quantity
        self.save()
        
        InventoryMovement.create(
            inventory_item=self,
            quantity=quantity,
            movement_type="SALE",
            reference="order"
        )


# InventoryReservation model: holds reserved stock info for customers
class InventoryReservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='reservations')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_reservations')
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Reservation {self.id} for {self.customer.full_name}, Product: {self.inventory_item.product.name}, Quantity: {self.quantity}"
    
    def has_expired(self):
        return timezone.now() >= self.expires_at
    
    def expire_reservation(self):
        if self.is_active:
            self.inventory_item.release_reserved_stock(self.quantity)
            self.is_active = False
            self.save()
            return True
        
    @staticmethod
    def create_reservation(inventory_item, customer, quantity, expires_at):
        inventory_item.reserve_stock(quantity)
        
        reservation = InventoryReservation.objects.create(
            inventory_item=inventory_item,
            customer=customer,
            quantity=quantity,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        InventoryReservation.save()
        return reservation


# Movement types enum
class MovementTypes(models.TextChoices):
    RESERVE = "RESERVE", "Reserve"
    RELEASE = "RELEASE", "Release"
    SALE = "SALE", "Sale"
    RESTOCK = "RESTOCK", "Restock"


# InventoryMovement model: logs stock movements and changes
class InventoryMovement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements')
    quantity = models.PositiveIntegerField()
    movement_type = models.CharField(max_length=10, choices=MovementTypes.choices)
    reference = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Movement {self.movement_type} of {self.quantity} for Product: {self.inventory_item.product.name}"
    
    @staticmethod
    def create(inventory_item, quantity, movement_type, reference):
        movement = InventoryMovement(
            inventory_item=inventory_item,
            quantity=quantity,
            movement_type=movement_type,
            reference=reference
        )
        movement.save()
        return movement
