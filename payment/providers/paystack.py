import requests
from django.conf import settings

from payment.models import PaymentStatus


class PaystackService:
    @staticmethod
    def initiate(payment):
        url = "https://api.paystack.co/transaction/initialize"
        
        payload = {
            "email": payment.order.user.email,
            "amount": int(payment.amount * 100),    # 100 because Paystack using pesewas
            "reference": payment.reference,
            "currency": payment.currency,
        }
        
        # Channel handling
        if payment.method.channel == "momo":
            payload["channels"] = ["mobile_money"]
        elif payment.method.channel == "card":
            payload["channels"] = ["card"]
        elif payment.method.channel == "bank":
            payload["channels"] = ["bank"]
            
        response = requests.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            },
            timeout=10
        )
        
        response.raise_for_status()
        data = response.json()["data"]
        
        # save provider reference
        payment.provider_reference = data.get("reference")
        payment.provider_response = data
        payment.status = PaymentStatus.PENDING
        payment.save(update_fields=[
            "provider_reference",
            "provider_response",
            "status"  
        ])
        
        return {
            "authorization_url": data["authorization_url"],
            "reference": payment.reference
        }
            
        
            