import json
import hmac
import hashlib
import logging

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Payment, PaymentEvent
from .services import PaymentService

logger = logging.getLogger(__name__)


class PayStackWebhookView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        payload = request.body
        signature = request.headers.get("x-paystack-signature")
        
        computed_hash = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode(),
            payload,
            hashlib.sha512
        ).hexdigest()
        
        if signature != computed_hash:
            return Response(status=400)
        
        data = json.loads(payload)
        event = data.get("event")
        reference = data.get("data", {}).get("reference")
        
        logger.info(f"Webhook event received: {event}")
        
        payment = None
        if reference:
            payment = Payment.objects.filter(reference=reference).first()
                
        PaymentEvent.objects.create(
            payment = payment,
            event_type = event,
            payload = data
        )
        
        if payment and payment.status == "success":
            return Response(status=200)
        
        if event == "charge.success" and reference:
            PaymentService.verify_payment(reference)
            
        return Response(status=200)

