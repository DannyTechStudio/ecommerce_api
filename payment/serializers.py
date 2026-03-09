from rest_framework import serializers
from .models import Payment, PaymentMethod


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ["id", "name", "code"]
        
        
class PaymentInitiateSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField()
    payment_method = serializers.CharField()
    
    
class PaymentSeralizer(serializers.ModelSerializer):
    method = serializers.CharField(source="method.name")
    
    class Meta:
        model = Payment
        fields = ["id", "reference", "amount", "currency", "status", "method", "created_at"]
        
        
class PaymentVerifySerializer(serializers.Serializer):
    reference = serializers.CharField()

