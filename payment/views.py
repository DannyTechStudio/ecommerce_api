from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Payment, PaymentMethod
from .services import PaymentService
from .permissions import IsStaffAdmin
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
    

class PaymentMethodAdminViewset(ModelViewSet):
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsStaffAdmin]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return PaymentMethod.objects.all()
        return PaymentMethod.objects.filter(is_active=True)
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active"])
        return Response(
            {"detail": "Payment method deactivated"}
        )
        
    
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
    permission_classes = [IsAuthenticated]
    lookup_field = "reference"
    
    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)


