import uuid
from django.db import transaction
from django.utils import timezone

import requests
from django.conf import settings

from .models import Payment, PaymentStatus
from .exceptions import PaymentVerification
from .providers.paystack import PaystackService

from catalog.models import Product
from order.models import Order, OrderStatus
from order.services import OrderService
from cart.models import Cart, CartStatus
from cart.services import CartService



class PaymentService:
    @staticmethod
    def generate_reference():
        reference = "PAY-" + uuid.uuid4().hex[:10].upper()
        return reference
    
    
    @staticmethod
    def generate_unique_reference():
        for _ in range(5):
            reference = PaymentService.generate_reference()
            if not Payment.objects.filter(reference=reference).exists():
                return reference
        raise RuntimeError("Unable to generate unique payment reference")
    
    
    @staticmethod
    def initiate_payment(order, method):
        # Validate order status
        if order.status != OrderStatus.PENDING:
            raise ValueError("Payment can be only made for pending orders")
        
        if Payment.objects.filter(order=order).exists():
            raise ValueError("Payment already exists for this order")
        
        # Validate payment method
        if not method.is_active:
            raise ValueError("Payment method is not active")
        
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            method=method,
            amount=order.total_price,
            currency="GHS",
            reference=PaymentService.generate_unique_reference(),
            provider_reference="",
            status=PaymentStatus.INITIATED,
        )
        
        # Provider routing
        if method.provider == "paystack":
            return PaystackService.initiate(payment)

        raise ValueError("Unsupported payment provider")
        
    

    @staticmethod
    @transaction.atomic
    def verify_payment(reference):
        payment = Payment.objects.select_for_update().select_related("order").get(reference=reference)
        
        if payment.status == PaymentStatus.SUCCESS:
            return payment
        
        if payment.status == PaymentStatus.FAILED:
            raise ValueError("Payment already failed")
        
        try:
            # Paystack Verification API Call
            response = requests.get(
                f"https://api.paystack.co/transaction/verify/{payment.reference}",
                headers={
                    "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
                },
                timeout=10
            )
        except requests.RequestException:
            raise PaymentVerification("Provider verification failed")
        
        response.raise_for_status()
        
        provider_response = response.json()
        
        data = provider_response.get("data", {})
        
        provider_status = data.get("status", "failed")
        
        # Update payment record based on provider response 
        # Successful payment
        if provider_status == "success":
            payment.status = PaymentStatus.PROCESSING
            payment.provider_reference = data.get("id")
            payment.provider_response = provider_response
            
            payment.save(update_fields=[
                "status",
                "provider_reference",
                "provider_response"
            ])
            
            return PaymentService.handle_successful_payment(payment.id) 
            
        # Failed payment
        else:
            payment.status = PaymentStatus.FAILED
            payment.provider_response = provider_response
            
            payment.save(update_fields=[
                "status", 
                "provider_response"
            ])
            
            return payment
    
    
    @staticmethod
    def expire_payment(payment):
        if payment.status in [PaymentStatus.INITIATED, PaymentStatus.PENDING]:
            payment.status = PaymentStatus.FAILED
            payment.save(update_fields=["status"])
            
    @staticmethod
    @transaction.atomic
    def handle_successful_payment(payment_id):
        payment = Payment.objects.select_for_update().select_related("order").get(id=payment_id)
        
        if payment.status == PaymentStatus.SUCCESS:
            return payment
        
        if payment.status not in [PaymentStatus.INITIATED, PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
            raise ValueError("Invalid payment state")
        
        order = Order.objects.select_for_update().get(id=payment.order_id)
                
        if order.status != OrderStatus.PENDING:
            raise ValueError("Invalid order state")
         
        cart = Cart.objects.select_for_update().get(id=order.cart_id)
        
        order_items = order.items.select_for_update().select_related("product")
        
        product_ids = [item.product_id for item in order_items]
        products = Product.objects.select_for_update().filter(id__in=product_ids)
        
        # Validate stock availability before marking payment as success
        for item in order_items:
            if item.product.quantity < item.quantity:
                payment.status = PaymentStatus.FAILED
                payment.save(update_fields=["status"])
                raise ValueError(f"Insufficient stock for {item.product.name}")
        
        # Deduct stock
        for item in order_items:
            product = item.product
            product.quantity -= item.quantity
            product.save(update_fields=["quantity"]) 
            
        # Mark payment as success
        payment.status = PaymentStatus.SUCCESS
        payment.paid_at = timezone.now()
        payment.save(update_fields=["status", "paid_at"])
        
        # Mark order as paid
        OrderService.mark_as_paid(order)
        
        # mark cart as consumed
        cart.status = CartStatus.CONSUMED
        cart.save(update_fields=["status"])
        
        # Create new active cart for user
        CartService.get_or_create_active_cart(order.user)
        
        return payment
    
    