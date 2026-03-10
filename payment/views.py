from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Payment, PaymentMethod
from .services import PaymentService
from .serializers import (
    PaymentMethodSerializer, 
    PaymentInitiateSerializer, 
    PaymentSeralizer, 
    PaymentVerifySerializer
)

from order.models import Order

# Create your views here.
class PaymentMethodListView(ListAPIView):
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    
    
class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PaymentInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order = Order.objects.get(
            id = serializer.validated_data["order_id"],
            user = request.user
        )
        
        method = PaymentMethod.objects.get(
            code = serializer.validated_data["payment_method"],
            is_active = True
        )
        
        payment = PaymentService.initiate_payment(order, method)
        
        return Response(PaymentSeralizer(payment).data)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PaymentVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment = PaymentService.verify_payment(serializer.validated_data["reference"])
        
        return Response(PaymentSeralizer(payment).data)


class PaymentDetailView(RetrieveAPIView):
    serializer_class = PaymentSeralizer
    lookup_field = "reference"
    
    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)


