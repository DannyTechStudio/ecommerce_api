from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from .models import Order
from .serializers import OrderSerializer

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
        