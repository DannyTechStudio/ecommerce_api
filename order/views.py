from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from .models import Order
from .serializers import OrderSerializer, CompleteOrderSerializer, CancelOrderSerializer

User = get_user_model()

# Create your views here.
class UserOrdersView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        orders = (
            Order.objects
            .filter(user=request.user)
            .prefetch_related("items")
            .order_by("-created_at")
        )
        
        serializer = OrderSerializer(orders, many=True)
        
        return Response(serializer.data)
        
        
class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, order_id):
        order = get_object_or_404(
            Order.objects.prefetch_related("items"),
            id=order_id,
            user=request.user
        )
        
        serializer = OrderSerializer(order)
        
        return Response(serializer.data)


class CompleteOrderView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, order_id):
        serializer = CompleteOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment_method_id = serializer.validated_data["payment_method_id"]

        from payment.models import PaymentMethod
        
        payment_method = get_object_or_404(
            PaymentMethod,
            id=payment_method_id
        )
        
        from .services import OrderService
        
        try:
            payment = OrderService.complete_order(
                user=request.user,
                order_id=order_id,
                payment_method=payment_method
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return Response(
            {
                "payment_reference": payment.reference,
                "payment_url": payment.payment_url,
            }
        )
        
        
class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, order_id):
        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user
        )
        
        from .services import OrderService
        
        try:
            OrderService.cancel_order(order)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return Response(
            {"message": "Order canceled"},
            status=status.HTTP_200_OK
        )


