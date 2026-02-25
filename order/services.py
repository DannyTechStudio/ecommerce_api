import uuid
from decimal import Decimal
from django.db import transaction

from cart.models import Cart, CartStatus

from .models import (
    OrderStatus, 
    Order, 
    OrderItem
)

class OrderService:
    @staticmethod
    def copy_shipping_snapshot(order, address):
        order.shipping_full_name = address.full_name
        order.shipping_street_address = address.street_address
        order.shipping_city = address.city
        order.shipping_state = address.state
        order.shipping_country = address.country
        order.shipping_phone = address.phone
    
    
    @staticmethod
    def generate_order_number():
        while True:
            number = "ORD-" + uuid.uuid4().hex[:10].upper()
            if not Order.objects.filter(order_number=number).exists():
                return number
    
    
    @staticmethod
    @transaction.atomic
    def create_order_from_cart(user, cart, address):
        # Validate user address ownership
        if address.user != user:
            raise ValueError("Address does not belong to user")
        
        # Validate user cart ownership
        if cart.user != user:
            raise ValueError("Cart does not belong to user")
        
        # Validate cart status
        if cart.status != Cart.CartStatus.CHECKED_OUT:
            raise ValueError("Cart must be checked out")
        
        # Validate that cart is not empty
        if not cart.items.exists():
            raise ValueError("Cart is empty")
        
        # Prevent duplicate order for the same cart
        if Order.objects.filter(cart=cart).exists():
            raise ValueError("Order already exists for this cart")
        
        # Obtain cart items
        items = list(cart.items.selected_related("product"))
        
        if not items:
            raise ValueError("Cannot create order from empty cart")
        
        # Compute total price using Decimal-safe accumulation
        total_price = sum(
            (item.quantity * item.price_snapshot for item in items),
            Decimal("0.00")
        )
        
        # Create order
        order = Order(
            order_number=OrderService.generate_order_number(),
            user=user,
            cart=cart,
            status = OrderStatus.PENDING,
            total_price=total_price,
            shipping_address=address,
        )
        
        # Cpoy shipping snapshot fields
        OrderService.copy_shipping_snapshot(order, address)
        order.save()
        
        # Create order item snapshots
        order_items = [
            OrderItem.objects.create(
                order=order,
                product_id=item.product.id,
                product_name=item.product.name,
                quantity=item.quantity,
                unit_price=item.price_snapshot,
                line_total=item.quantity * item.price_snapshot
            )
            for item in items
        ]
        
        OrderItem.objects.bulk_create(order_items)
        
        return order
        
        
        