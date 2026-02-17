from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from .models import Cart
from .serializers import CartSerializer
from .admin_permissions import IsAdminUserOnly
from inventory.services import cancel_reservation


class AdminCartListView(APIView):
    permission_classes = [IsAdminUserOnly]
    
    def get(self, request):
        user_id = request.query_params.get("user_id")
        
        if user_id:
            carts = Cart.objects.filter(user_id=user_id)
        else:
            carts = Cart.objects.all()
            
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class AdminCartDetailView(APIView):
    permission_classes = [IsAdminUserOnly]
    
    def get(self, request, cart_id):
        cart = get_object_or_404(Cart, id=cart_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
"""
    Permit Admin to manually expire a cart
"""
class AdminExpireCartView(APIView):
    permission_classes = [IsAdminUserOnly]
    
    def post(self, request, cart_id):
        cart = get_object_or_404(Cart, id=cart_id)
        cart.mark_expired()
        cart.save()
        
        return Response(
            {"message": "Cart expired successfully"},
            status=status.HTTP_200_OK
        )
        

"""
    Permit Admin to manually release item reservations
"""
class AdminReleaseCartReservationView(APIView):
    permission_classes = [IsAdminUserOnly]
    
    def post(self, request, cart_id):
        cart = get_object_or_404(Cart, id=cart_id)
        
        for item in cart.items.all():
            cancel_reservation(item.reservation)
            
        return Response(
            {"message": "Reservations released successfully"},
            status=status.HTTP_200_OK
        )