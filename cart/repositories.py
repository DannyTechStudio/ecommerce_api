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
    def find_item(self, cart, product):
        return (CartItem.objects.filter(cart=cart, product=product).first())
        
    
    def add_item(self, cart_item):
        cart_item.save()
        
        return cart_item
    
    
    def delete_item(self, cart_item):
        cart_item.delete()
        
    
    def list_items(self, cart):
        return Cart.objects.filter(cart=cart)