from django.utils import timezone
from .models import CartStatus


# Base validation error for cart domain
class CartValidationError(ValueError):
    pass


"""
    Cart state validators
"""
# Ensuring cart is usable for operations
def validate_cart_is_active(cart):
    if cart.status != CartStatus.ACTIVE:
        raise CartValidationError("Cart is not active")
    
    if cart.expires_at is None:
        raise CartValidationError("Cart has no expiration time")
    
    if timezone.now() >= cart.expires_at:
        raise CartValidationError("Cart has expired")
    
    
# Prevent modification of checked out carts
def validate_cart_not_checked_out(cart):
    if cart.status == CartStatus.CHECKED_OUT:
        raise CartValidationError("Cannot modify a checked out cart")
    

# Prevent operations on expired carts
def validate_cart_not_expired(cart):
    if cart.status == CartStatus.EXPIRED:
        raise CartValidationError("Cannot modify an expired cart")


"""
    Quantity validators
"""

# Ensuring quantity is greater than zero
def validate_positive_quantity(quantity):
    if quantity <= 0:
        raise CartValidationError("Quantity must be positive")
    
    
# Ensuring quantity is zero or greater
def validate_non_negative_quantity(quantity):
    if quantity < 0:
        raise CartValidationError("Quantity cannot be negative")
    
    
# Prevent reducing quantity below zero
def validate_quantity_not_exceeding(current_quantity, requested_reduction):
    if requested_reduction > current_quantity:
        raise CartValidationError("Cannot reduce quantity below zero")
    
    
"""
    Cart item validators
"""
# Ensuring cart item exists before operations
def validate_cart_item_exists(item):
    if item is None:
        raise CartValidationError("Cart item does not exist")
    

# Ensuring cart item has a valid inventory reservation
def validate_reservation_exists(reservation):
    if reservation is None:
        raise CartValidationError("Cart item has no inventory reservation")
    
    
# Ensuring price snapshot is valid
def validate_price_snapshot(price):
    if price is None:
        raise CartValidationError("Price snapshot is required")
    
    if price < 0:
        raise CartValidationError("Price cannot negative")
