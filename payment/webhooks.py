import json
import hmac
import hashlib

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Payment, PaymentEvent
from .services import PaymentService


class PayStackWebhookView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        payload = request.body
        signature = request.headers.get("x-paystack-signature")
        
        computed_hash = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode(),
            payload,
            hashlib.sha3_512
        ).hexdigest()
        
        if signature != computed_hash:
            return Response(status=400)
        
        data = json.loads(payload)
        
        event = data.get("event")
        
        reference = data.get("data", {}).get("reference")
        
        payment = None
        
        if reference:
            try:
                payment = Payment.objects.get(reference=reference)
            except Payment.DoesNotExist:
                payment = None
                
        PaymentEvent.objects.create(
            payment = payment,
            event_type = event,
            payload = data
        )
        
        if event == "charge.success" and reference:
            PaymentService.verify_payment(reference)
            
        return Response(status=200)

