from django.db import transaction
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser

from catalog.models import Product
from .models import Cart, CartItem, CartStatus

from order.services import OrderService

class CartService:
    # Cart TTL and extension in hours
    TTL_HOURS = timedelta(hours=360)
    EXTENSION_HOURS = timedelta(hours=12)
    
    
    @staticmethod
    def _ensure_authenticated(user):
        if isinstance(user, AnonymousUser):
            raise ValueError("Signup required")
    
    
    @staticmethod
    def get_or_create_active_cart(user):
        """
            Returns active cart or creates a new one if expired or None
        """
        cart = (
            Cart.objects
            .select_for_update()
            .filter(user=user, status=CartStatus.ACTIVE)
            .first()
        )
        
        # Expire cart if past TTL
        if cart and cart.expires_at < timezone.now():
            cart.status = CartStatus.EXPIRED
            cart.save()
            cart = None
        
        # Create cart if None exsits and return as ACTIVE
        if not cart:
            cart = Cart.objects.create(
                user=user,
                status=CartStatus.ACTIVE,
                expires_at=timezone.now() + CartService.TTL_HOURS
            )
        
        return cart
    
    
    @staticmethod
    def extend_cart_ttl(cart):
        cart.expires_at = timezone.now() + CartService.EXTENSION_HOURS
        cart.save()
    
    
    @staticmethod
    @transaction.atomic
    def add_to_cart(user, product_id, quantity):
        # Get product and product price
        product = Product.objects.filter(id=product_id, is_active=True).first()
        price = product.price
        
        # Validates product exists
        if not product:
            raise ValueError("Product not found or inactive.")
        
        # Validates quantity
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        
        # Get or create active cart
        cart = CartService.get_or_create_active_cart(user)
        
        # lock cart row
        cart = (
            Cart.objects
            .select_for_update()
            .get(id=cart.id)
        )
        
        # Create new cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': quantity,
                "price_snapshot": price
            }
        )
        
        # if item exists increase its quantity
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
            
        # Then extend cart time-to-live duration and return it
        CartService.extend_cart_ttl(cart)
        
        return cart
    
    
    @staticmethod
    def lock_cart(cart):
        cart.status = CartStatus.LOCKED
        cart.locked_at = timezone.now()
        cart.save(update_fields=["status", "locked_at"])
        
        
    @staticmethod
    def consume_cart(cart):
        cart.status = CartStatus.CONSUMED
        cart.save(update_fields=["status"])
        
    
    @staticmethod
    def restore_cart(cart):
        if cart.status != CartStatus.LOCKED:
            raise ValueError("Only locked cart can be restored")
        
        cart.status = CartStatus.ACTIVE
        cart.locked_at = None
        cart.save(update_fields=["status", "locked_at"])
        
        
    @staticmethod
    def expire_cart(cart):
        if cart.status != CartStatus.ACTIVE:
            raise ValueError("Cart not found or locked")
        
        if cart.expires_at < timezone.now():
            cart.status = CartStatus.EXPIRED
            cart.save(update_fields=["status"])
    
    
    @staticmethod
    @transaction.atomic
    def checkout_cart(user, address):
        """
            Transition active cart to checked out after validating stock 
        """
        
        # Fetch active cart with row-level lock
        cart = (
            Cart.objects
            .select_for_update()
            .filter(user=user, status=CartStatus.ACTIVE)
            .first()
        )
            
        if not cart:
            raise ValueError("No active cart found.")
        
        # Expiry check
        if cart.expires_at < timezone.now():
            cart.status = CartStatus.EXPIRED
            cart.save(update_fields=["status"])
            raise ValueError("Cart expired")
        
        # Lock cart items + products in one query
        items = list(cart.items.select_related("product").select_for_update())
        
        if not items:
            raise ValueError("Cart is empty")
        
        # Validate stock availability
        for item in items:
            if item.quantity > item.product.quantity:
                raise ValueError(f"Insufficient stock for {item.product.name}")
            
        # Lock cart
        cart.status = CartStatus.LOCKED
        cart.locked_at = timezone.now()
        cart.save(update_fields=["status", "locked_at"])
        
        # Create order from locked cart
        order = OrderService.create_order_from_cart(
            user=user,
            cart=cart,
            address=address
        )
        
        return {
            "order": order, 
            "cart": cart, 
        }
