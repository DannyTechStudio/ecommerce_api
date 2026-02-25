from django.db import transaction
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser

from catalog.models import Product
from .models import Cart, CartItem, CartStatus

from order.services import OrderService

class CartService:
    # Cart TTL and extension in hours
    TTL_HOURS = 22
    EXTENSION_HOURS = 15
    
    
    @staticmethod
    def _ensure_authenticated(user):
        if isinstance(user, AnonymousUser):
            raise ValueError("Signup required")
    
    
    @staticmethod
    def get_active_cart(user):
        """
            Returns active cart or creates a new one if expired or None
        """
        cart = Cart.objects.filter(user=user, status=CartStatus.ACTIVE).first()
        
        # Expire cart if past TTL
        if cart and cart.expires_at < timezone.now():
            cart.expires_at = CartStatus.EXPIRED
            cart.save()
            cart = None
        
        # Create cart if None exsits and return as ACTIVE
        if not cart:
            cart = Cart.objects.create(
                user=user,
                status=CartStatus.ACTIVE,
                expires_at=timezone.now() + timedelta(hours=CartService.TTL_HOURS)
            )
        
        return cart
    
    
    @staticmethod
    def extend_cart_ttl(cart):
        cart.expires_at = timezone.now() + timedelta(hours=CartService.EXTENSION_HOURS)
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
        cart = CartService.get_active_cart(user)
        
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
            
            Cart.objects.create(
                user=user,
                status=CartStatus.ACTIVE,
                expires_at= timezone.now() + timezone.timedelta(hours=CartService.TTL_HOURS)
            )
            
            raise ValueError("Cart expired. New active cart created.")
        
        # Lock cart items + products in one query
        items = list(cart.items.select_related("product").select_for_update())
        
        if not items:
            raise ValueError("Cart is empty")
        
        # Validate stock availability
        unavailable_items = [
            item.product.name
            for item in items
            if item.quantity > item.product.quantity
        ]
                
        if unavailable_items:
            raise ValueError(f"Stock insufficient for: {', '.join(unavailable_items)}")
        
        # Deduct stock
        for item in items:
            product = item.product
            product.quantity -= item.quantity
            product.save(update_fields=["quantity"])
            
        # Mark cart as checked out
        cart.status = CartStatus.CHECKED_OUT
        cart.save(update_fields=["status"])
        
        # Create order from checked out cart
        order = OrderService.create_order_from_cart(
            user=user,
            cart=cart,
            address=address
        )
        
        # Create new empty active cart
        new_cart = Cart.objects.create(
            user=user,
            status=CartStatus.ACTIVE,
            expires_at=timezone.now() + timezone.timedelta(hours=CartService.TTL_HOURS)
        )
        
        return {
            "order": order, 
            "checked_out_cart": cart, 
            "active_cart": new_cart,
        }
    
    
    @staticmethod
    def get_checked_out_cart(user):
        cart = Cart.objects.filter(user=user, status=CartStatus.CHECKED_OUT).order_by("-created_at").first()
        
        if not cart:
            raise ValueError("No checked-out cart found")
        
        return cart