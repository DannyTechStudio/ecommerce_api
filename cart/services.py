from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser

from catalog.models import Product
from .models import Cart, CartItem, CartStatus

from order.services import OrderService

class CartService:
    # Cart TTL and extension in hours
    CART_TTL = timezone.timedelta(hours=168)
    CART_EXTENSION = timezone.timedelta(hours=12)
    CART_LOCK_TTL = timezone.timedelta(minutes=15)
    
    
    @staticmethod
    def _ensure_authenticated(user):
        if isinstance(user, AnonymousUser):
            raise ValueError("Signup required")
    
    
    @staticmethod
    def auto_restore_locked_cart(cart):
        if cart.status == CartStatus.LOCKED and cart.locked_at and cart.locked_at + CartService.CART_LOCK_TTL < timezone.now():
            cart.status = CartStatus.ACTIVE
            cart.locked_at = None
            cart.save(update_fields=["status", "locked_at"])
    
    
    @staticmethod
    @transaction.atomic
    def get_or_create_active_cart(user):
        """
            Returns active cart or creates a new one if expired or None
        """
        CartService._ensure_authenticated(user)
        
        cart = (
            Cart.objects
            .select_for_update()
            .filter(user=user, status=CartStatus.ACTIVE)
            .first()
        )
        
        # Expire cart if past TTL
        if cart and cart.expires_at < timezone.now():
            cart.status = CartStatus.EXPIRED
            cart.save(update_fields=["status"])
            cart = None
        
        # Create cart if None exsits and return as ACTIVE
        if not cart:
            cart = Cart.objects.create(
                user=user,
                status=CartStatus.ACTIVE,
                expires_at=timezone.now() + CartService.CART_TTL
            )
        
        return cart
    
    
    @staticmethod
    def extend_cart_ttl(cart):
        cart.expires_at += CartService.CART_EXTENSION
        cart.save(update_fields=["expires_at"])
    
    
    @staticmethod
    @transaction.atomic
    def add_to_cart(user, product_id, quantity):
        CartService._ensure_authenticated(user)
        
        # Validates quantity
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        
        # Get product and product price
        product = Product.objects.select_for_update().filter(id=product_id, is_active=True).first()
        
        # Validates product exists
        if not product:
            raise ValueError("Product not found or inactive.")
        
        # Validate stock
        if quantity > product.quantity:
            raise ValueError("Insufficient stock available.")
        
        # Get or create active cart
        cart = CartService.get_or_create_active_cart(user)
        
        # lock cart row
        cart = Cart.objects.select_for_update().get(id=cart.id)
        
        # Create new cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': quantity,
                "price_snapshot": product.price
            }
        )
        
        # if item exists increase its quantity
        if not created:
            new_quantity = cart_item.quantity + quantity
            
            if new_quantity > product.quantity:
                raise ValueError("Insufficient stock available.")
            
            cart_item.quantity = new_quantity
            cart_item.save(update_fields=["quantity"])
            
        # Then extend cart time-to-live duration and return it
        CartService.extend_cart_ttl(cart)
        
        return cart
    
    
    @staticmethod
    def lock_cart(cart):
        cart.status = CartStatus.LOCKED
        cart.locked_at = timezone.now()
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
        CartService._ensure_authenticated(user)
        
        # Fetch active cart with row-level lock
        cart = (
            Cart.objects
            .select_for_update()
            .filter(user=user, status=CartStatus.ACTIVE)
            .first()
        )
        
        # Validate cart exixts   
        if not cart:
            raise ValueError("No active cart found.")
        
        # Expiry check
        if cart.expires_at < timezone.now():
            cart.status = CartStatus.EXPIRED
            cart.save(update_fields=["status"])
            raise ValueError("Cart expired")
        
        # Lock cart items + products in one query
        items = list(cart.items.select_related("product").select_for_update(of=("self", "product")))
        
        # validate cart has items
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


    @staticmethod
    @transaction.atomic
    def consume_cart(cart):
        cart = Cart.objects.select_for_update().get(id=cart.id)
        
        if cart.status != CartStatus.LOCKED:
            raise ValueError("Only locked cart be consumed.")
        
        cart.status = CartStatus.CONSUMED
        cart.save(update_fields=["status"])
        
        
    @staticmethod
    @transaction.atomic
    def restore_cart(cart):
        cart = Cart.objects.select_for_update().get(id=cart.id)
        
        if cart.status != CartStatus.LOCKED:
            raise ValueError("Only locked cart can be restored")
        
        cart.status = CartStatus.ACTIVE
        cart.locked_at = None
        cart.save(update_fields=["status", "locked_at"])


    @staticmethod
    @transaction.atomic
    def update_cart_item(item, quantity):
        product = Product.objects.select_for_update().get(id=item.product_id)
        
        if quantity > product.quantity:
            raise ValueError("Insufficient stock")
        
        item.quantity = quantity
        item.save(update_fields=["quantity"])
        
        CartService.extend_cart_ttl(item.cart)
        
        return item.cart
    
    
    @staticmethod
    @transaction.atomic
    def remove_cart_item(item):
        cart = item.cart
        item.delete()
        
        CartService.extend_cart_ttl(cart)
        
        return cart 