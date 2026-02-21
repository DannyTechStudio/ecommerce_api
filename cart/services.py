from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser

from catalog.models import Product
from .models import Cart, CartItem


class CartService:
    @staticmethod
    def _ensure_authenticated(user):
        if isinstance(user, AnonymousUser):
            raise ValueError("Signup required")
    
    @staticmethod
    def get_active_cart(user):
        """
            Returns active cart or creates a new one if expired or None
        """
        cart = Cart.objects.filter(user=user, status='ACTIVE').first()
        now = timezone.now()
        
        if cart:
            if cart.expires_at < now:
                cart.expires_at = 'EXPIRED'
                cart.save()
                cart = None
                
        if not cart:
            cart = Cart.objects.create(user=user)
        return cart
    
    
    @staticmethod
    @transaction.atomic
    def add_to_cart(user, product_id, quantity):
        product = Product.objects.filter(id=product_id, is_active=True).first()
        
        price = product.price
        
        if not product:
            raise ValueError("Product not found or inactive.")
        
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        
        cart = CartService.get_active_cart(user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': quantity,
                "price_snapshot": price
            }
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
            
            
        cart.extend_ttl()
        return cart
    
    
    @staticmethod
    @transaction.atomic
    def checkout_cart(user):
        """
            Transition active cart to checked out after validating stock 
        """
        cart = CartService.get_active_cart(user)
        
        if cart.status != "ACTIVE":
            raise ValueError("Cart is not active")
        
        if not cart.items.exists():
            raise ValueError("Cart is empty")
        
        # Stock validation
        unavailable_items = []
        for item in cart.items.select_related('product'):
            if item.quantity > item.product.quantity:
                unavailable_items.append(item.product.name)
                
        if unavailable_items:
            raise ValueError(f"Stock insufficient for: {', '.join(unavailable_items)}")
        
        # Deduct stock
        for item in cart.items.select_related('product'):
            item.product.quantity -= item.quantity
            item.product.save()
            
        # Mark cart as checked out
        cart.status = 'CHECKED_OUT'
        cart.save()
        return cart