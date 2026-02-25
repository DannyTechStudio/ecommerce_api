from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model

from cart.services import CartService
from accounts.models import Address

from .models import Order
from .serializers import OrderSerializer

User = get_user_model()

# Create your views here.
class UserOrdersView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        
        return Response(
            OrderSerializer(orders, many=True).data
        )
        
        
class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, order_id):
        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user
        )
        
        return Response(
            OrderSerializer(order).data
        )