import json
import hmac
import hashlib
import logging

from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

from .models import Payment, PaymentEvent
from .services import PaymentService

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class PayStackWebhookView(View):
    def post(self, request):
        # logger.info(f"Webhook event: {event} | Ref: {reference}")
        print("webook hit view")
        
        payload = request.body
        signature = request.headers.get("x-paystack-signature")
        
        computed_hash = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode(),
            payload,
            hashlib.sha512
        ).hexdigest()
        
        if not hmac.compare_digest(signature or "", computed_hash):
            logger.warning("Invalid webhook signature")
            return HttpResponse(status=400)
        
        data = json.loads(payload)
        event = data.get("event")
        reference = data.get("data", {}).get("reference")
        
        logger.info(f"Webhook event received: {event}")
        
        payment = None
        if reference:
            payment = Payment.objects.filter(reference=reference).first()
            
        if not payment:
            logger.warning(f"No payment found for reference: {reference}")
            
        # store event
        PaymentEvent.objects.create(
            payment=payment,
            event_type=event,
            payload=data
        )
        
        # Handle successful payment
        if event == "charge.success" and reference:
            if payment:
                PaymentService.verify_payment(reference)
            else:
                logger.warning(f"Skipping verification, payment not found: {reference}")
            
        return HttpResponse(status=200)

