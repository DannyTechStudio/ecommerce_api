from datetime import datetime, timedelta
from .models import InventoryItem, InventoryReservation


# Checkout flow
def customer_adds_product_to_cart(customer, product, quantity):
    inventory_item = InventoryItem.objects.get(product=product)
    inventory_item.reserve_stock(quantity)
    customer = customer
    
    reservation = InventoryReservation(
        inventory_item=inventory_item,
        customer=customer,
        quantity=quantity,
        created_at = datetime.now(),
        expires_at = datetime.now() + timedelta(hours=24)
    )
    reservation.save()
    return reservation

def customer_completes_payment(reservation):
    if reservation.is_active:
        reservation.inventory_item.deduct_stock(reservation.quantity)
        reservation.is_active = False
        reservation.save()
        return True
    
def reservation_expires(reservation):
    reservation.expire_reservation()
