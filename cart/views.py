from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from .services import CartService
from .models import CartItem
from .serializers import (
    CartSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer, 
)


# Create your views here.
class CartView(APIView):
    permission_classes = [IsAuthenticated]
    """ 
    Get current active cart or auto-create
    """
    def get(self, request):
        cart = CartService.get_active_cart(request.user)
        return Response(CartSerializer(cart).data)
    
    
class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart = CartService.add_to_cart(
            user=request.user,
            product_id=serializer.validated_data["product_id"],
            quantity=serializer.validated_data["quantity"],
        )
        
        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_200_OK
        )
        
        
class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        item = get_object_or_404(
            CartItem,
            id=item_id,
            cart__user=request.user,
            cart__status="ACTIVE",
        )
        
        item.quantity = serializer.validated_data["quantity"]
        item.save()
        
        item.cart.extend_ttl()
        return Response({"message": "Item updated"})
    
    
class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        item = get_object_or_404(
            CartItem,
            id=item_id,
            cart__user=request.user,
            cart__status="ACTIVE",
        )
        
        cart = item.cart
        item.delete()
        cart.extend_ttl
        
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
        
        
class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = CartService.checkout_cart(request.user)
        return Response({
            "message": "Checkout successful",
            "cart_id": cart.id
        })