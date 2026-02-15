from django.db import transaction
from django.utils import timezone

from catalog.models import Product
from .models import CartStatus
from .repositories import CartRepository, CartItemRepository

from inventory.services import (
    create_reservation,
    complete_payment,
    cancel_reservation,
    release_expired_reservations
)


class CartService:
    @staticmethod
    def get_or_create_active_cart(user):
        cart = CartRepository.find_active_cart_by_user(user=user)
        
        if cart is None:
            return CartRepository.create_cart(user=user)
            
        if not cart.is_active():
            cart.mark_expired()
            cart.save()
            
            items = CartItemRepository.get_item_by_cart(cart)
            for item in items:
                cancel_reservation(item.reservation)
                
            return CartRepository.create_cart(user=user)
        
        return cart
    
    
    @staticmethod
    @transaction.atomic
    def add_product_to_cart(user, product_id, quantity):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        cart = CartService.get_or_create_active_cart(user)
        product = Product.objects.filter(id=product_id)
        existing_item = CartItemRepository.find_item(cart=cart, product=product)
        
        if existing_item:
            reservation = existing_item.reservation
            
            create_reservation(
                inventory_item=reservation.inventory_item,
                quantity=quantity,
                reference=f"cart: {cart.id}"
            )
            
            existing_item.increase_quantity(quantity)
            existing_item.save()
            
            cart.extend_expiration(ttl_minutes=30)
            cart.save()
            
        reservation = create_reservation(
            inventory_item=product.inventory_item,
            quantity=quantity,
            reference=f"cart: {cart.id}"
        )
        
        item = CartItemRepository.create_item(
            cart=cart,
            product=product,
            quantity=quantity,
            price_snapshot=product.price,
            reservation=reservation
        )
        
        cart.extend_expiration(ttl_minutes=30)
        cart.save()
        
        return item
    
    
    @staticmethod
    @transaction.atomic
    def update_item_quantity(user, product_id, new_quantity):
        if new_quantity < 0:
            raise ValueError("Quantity cannot be negative")
        
        cart = CartService.get_or_create_active_cart(user=user)
        product = Product.objects.get(id=product_id)
        
        item = CartItemRepository.find_item(cart=cart, product=product)
        
        if item is None:
            raise ValueError("Item is not in cart")
        
        if new_quantity == 0:
            return CartService.remove_item_from_cart(user, product_id)
        
        current_quantity = item.quantity
        diff = new_quantity - current_quantity
        
        if diff > 0:
            create_reservation(
                inventory_item=item.reservation.inventory_item,
                quantity=diff,
                reference=f"cart: {cart.id}"
            )
            
            item.increase_quantity(diff)
        elif diff < 0:
            cancel_reservation(item.reservation, quantity=abs(diff))
            item.decrease_quantity(abs(diff))
            
        item.save()
        
        cart.extend_expiration(ttl_minutes=30)
        cart.save()
        
        return item
    
    
    @staticmethod
    @transaction.atomic
    def remove_item_from_cart(user, product_id):
        cart = CartService.get_or_create_active_cart(user=user)
        product = Product.objects.get(id=product_id)
        
        item = CartItemRepository.find_item(cart=cart, product=product)
        
        if item is None:
            raise ValueError("Item is not in cart")
        
        cancel_reservation(item.reservation)
        CartItemRepository.delete_item(item)
        
        cart.extend_expiration(ttl_minutes=30)
        cart.save()
        
    
    @staticmethod
    @transaction.atomic
    def checkout_cart(user):
        cart = CartService.get_or_create_active_cart(user=user)
        items = CartItemRepository.get_item_by_cart(cart=cart)
        
        if not items:
            raise ValueError("Cannot checkout empty cart")
        
        for item in items:
            complete_payment(item.reservation)
            
        cart.mark_checked_out()
        cart.save()
        
        return {
            "cart_id": cart.id,
            "status": "checked_out",
            "total_items": len(items)
        }
    
    