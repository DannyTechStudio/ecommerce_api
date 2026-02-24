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
from .services import OrderService

User = get_user_model()

# Create your views here.
class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """ 
            Create order from the user's checked-out cart 
            Requires address_id in request body 
        """
        address_id = request.data.get("address_id")
        if not address_id:
            return Response(
                {"detail:": "Address ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        address = get_object_or_404(Address, id=address_id, user=request.user)
        cart = CartService.get_checked_out_cart(request.user)
        
        order = OrderService.create_order_from_cart(
            user=request.user,
            cart=cart,
            address=address
        )
        
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )
    

class UserOrdersView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        
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