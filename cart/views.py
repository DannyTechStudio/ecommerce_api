from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    CartSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
    RemoveCartItemSerializer
)

from .services import CartService
from .exceptions import CartError


# Create your views here.
class CartView(APIView):
    """
        GET -> Retrieve current user's active cart 
    """
    def get(self, request):
        try:
            cart = CartService.get_or_create_active_cart(request.user)
            serializer = CartSerializer(cart)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except CartError as e:
            return Response(
                {"error": type(e).__name__, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            

class AddToCartView(APIView):
    """
        POST -> Add product to cart
    """
    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            CartService.add_product_to_cart(
                user=request.user,
                product_id=serializer.validated_data["product_id"],
                quantity=serializer.validated_data["quantity"]
            )
            
            return Response(
                {"message": "Product added to cart"},
                status=status.HTTP_200_OK
            )
            
        except CartError as e:
            return Response(
                {"error": type(e).__name__, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class UpdateCartItemView(APIView):
    """
        PATCH -> Update quantity of an item 
    """
    def patch(self, request):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            CartService.update_item_quantity(
                user=request.user,
                product_id=serializer.validated_data["product_id"],
                new_quantity=serializer.validated_data["quantity"]
            )
            
            return Response(
                {"message": "Cart item updated"},
                status=status.HTTP_200_OK
            )
            
        except CartError as e:
            return Response(
                {"error": type(e).__name__, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
            
class RemoveCartItemView(APIView):
    """
        DELETE -> Remove item from cart 
    """
    def delete(self, request):
        serializer = RemoveCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try: 
            CartService.remove_item_from_cart(
                user=request.user,
                product_id=serializer.validated_data["product_id"]
            )
            
            return Response(
                {"message": "Item removed from cart"},
                status=status.HTTP_204_NO_CONTENT
            )
        
        except CartError as e:
            return Response(
                {"error": type(e).__name__, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
            
class CheckoutCartView(APIView):
    """
        POST -> Checkout active cart 
    """
    def post(self, request):
        try:
            result = CartService.checkout_cart(request.user)
            
            return Response(result, status=status.HTTP_200_OK)
        
        except CartError as e:
            return Response(
                {"error": type(e).__name__, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )