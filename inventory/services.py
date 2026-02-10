from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from .models import InventoryItem, InventoryReservation


# Customer actions
def create_reservation(customer, product, quantity, expiration_hours=24):
    with transaction.atomic():
        inventory_item = (
            InventoryItem.objects.select_for_update().get(product=product)
        )
        
        if quantity <= 0:
            raise ValueError("Quantity must be greater then zero")
        
        if quantity > inventory_item.available_quantity():
            raise ValueError("Insufficient stock available")
        
        inventory_item.reserve_stock(quantity)
        
        reservation = InventoryReservation.objects.create(
            inventory_item = inventory_item,
            customer = customer,
            quantity=quantity,
            expires_at = timezone.now() + timezone.timedelta(hours=expiration_hours)
        )
        
        return reservation

# Customer completes payment, stock deducted permanently
def complete_payment(reservation):
    if not reservation.is_active:
        return False
    
    with transaction.atomic():
        inventory_item = InventoryItem.objects.select_for_update().get(id=reservation.inventory_item.id)

        inventory_item.deduct_stock(reservation.qunatity)
        
        reservation.is_active = False
        reservation.save(updated_fields=["is_active"])
        
        return True


# Customer cancels reservation
def cancel_reservation(reservation):
    if not reservation.is_active:
        return False
    
    with transaction.atomic():
        inventory_item = (
            InventoryItem.objects.select_for_update().get(id=reservation.inventory_item.id)
        )
        
        inventory_item.release_reserved_stock(reservation.quantity)
        
        reservation.is_active = False
        reservation.save(update_fields=["is_active"])
        
        return True
    

"""
System maintenance task.
Finds and releases all expired reservations safely.

Returns:
    dict: summary of processing results
"""

def release_expired_reservations():
    now = timezone.now()
    
    expired_reservations = (
        InventoryReservation.objects.select_related("inventory_item").filter(is_active=True, expires_at_lt=now)
    )
    
    processed = 0
    failed = 0
    
    for reservation in expired_reservations:
        try:
            with transaction.atomic():
                inventory_item = InventoryItem.objects.select_for_update().get(id=reservation.inventory_item.id)
                
                inventory_item.release_reserved_stock(reservation.quantity)
                
                reservation.is_active = False
                reservation.save(update_fields=["is_active"])
                
                processed += 1
        except Exception:
            failed += 1
            
    return {
        "expired_reservation_found": expired_reservations.count(),
        "released": processed,
        "failed": failed
    }
