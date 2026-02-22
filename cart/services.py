from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser

from catalog.models import Product
from .models import Cart, CartItem


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
        cart = Cart.objects.filter(user=user, status='ACTIVE').first()
        now = timezone.now()
        
        # Expire cart if past TTL
        if cart and cart.expires_at < now:
            cart.expires_at = 'EXPIRED'
            cart.save()
            cart = None
        
        # Create cart if None exsits and return as ACTIVE
        if not cart:
            cart = Cart.objects.create(
                user=user,
                status="ACTIVE",
                expires_at=now + timezone.timedelta(hours=CartService.TTL_HOURS)
            )
        
        return cart
    
    
    @staticmethod
    def extend_cart_ttl(cart):
        cart.expires_at = timezone.now() + timezone.timedelta(hours=CartService.EXTENSION_HOURS)
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
    def checkout_cart(user):
        """
            Transition active cart to checked out after validating stock 
        """
        cart = Cart.objects.filter(user=user, status="ACTIVE").first()
        
        if not cart:
            raise ValueError("No active cart found.")
        
        if cart.expires_at < timezone.now():
            cart.status = "EXPIRED"
            cart.save()
            cart = Cart.objects.create(user=user)
            raise ValueError("Cart expired. New active cart created.")
        
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
        
        # Auto-create new empty active cart
        new_cart = Cart.objects.create(
            user=user,
            status='ACTIVE',
            expires_at=timezone.now() + timezone.timedelta(hours=CartService.TTL_HOURS)
        )
        
        return cart, new_cart