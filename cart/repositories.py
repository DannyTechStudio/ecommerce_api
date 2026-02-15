from django.utils import timezone
from django.db import IntegrityError

from .models import Cart, CartItem, CartStatus


class CartRepository:
    def find_active_cart_by_user(self, user):
        return (
            Cart.objects.filter(user=user, status=CartStatus.ACTIVE).first()
        )


    def create_cart(self, user, ttl_minutes):
        expires_at = timezone.now() + timezone.timedelta(minutes=ttl_minutes)
        
        cart = Cart(user=user, expires_at=expires_at)
        
        try:
            cart.save()
        except IntegrityError:
            raise
        
        return cart
    
    
    def save(self, cart):
        cart.save()
        
        return cart
    
    
    def find_expired_cart(self, now=None):
        if now is None:
            now = timezone.now()
            
        return Cart.objects.filter(status=CartStatus.ACTIVE, expires_at__lt=now)
        

class CartItemRepository:
    @staticmethod
    def find_item(cart, product):
        return (CartItem.objects.filter(cart=cart, product=product).first())
    
    @staticmethod
    def create_item(cart, product, quantity, price_snapshot, reservation):
        cart_item = CartItem(
            cart=cart,
            product=product,
            quantity=quantity,
            price_snapshot=price_snapshot,
            reservation=reservation
        )
        cart_item.save()
        return cart_item
    
        
    @staticmethod
    def add_item(cart_item):
        cart_item.save()
        
        return cart_item
    
    @staticmethod
    def delete_item(cart_item):
        cart_item.delete()
        
    @staticmethod
    def get_item_by_cart(cart):
        return CartItem.objects.filter(cart=cart)