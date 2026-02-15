"""
    Base exception for all cart domain errors
"""
class CartError(Exception):
    default_message = "Cart operation failed"
    
    def __init__(self, message=None):
        super().__init__(message or self.default_message)
        
        
"""
    Cart state errors
"""
class CartNotActiveError(CartError):
    default_message = "Cart is not active"
    
    
class CartExpiredError(CartError):
    default_message = "Cart has expired"

    
class CartCheckOutError(CartError):
    default_message = "Cart has already been checked out"
    

class EmptyCartCheckOutError(CartError):
    default_message = "Cannot check out empty cart"



"""
    Cart item errors
"""
class CartItemNotFoundError(CartError):
    default_message = "Cart item not found"
    
    
class InvalidQuantityError(CartError):
    default_message = "Invalid quantity value"
    
    
class QuantityReductionError(CartError):
    default_message = "Cannot reduce quantity below zero"
    
    

"""
    Reservation errors
"""
class ReservationMissingError(CartError):
    default_message = "Cart item is missing inventory reservation"
    

class ReservationSyncError(CartError):
    default_message = "Cart quantity and reservation are mismatched"
    


"""
    Pricing errors
"""
class InvalidPriceSnapshotError(CartError):
    default_message = "Invalid price snapshot"