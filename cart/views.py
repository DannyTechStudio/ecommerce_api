from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    CartSerializer,
    CartItemSerializer,
    AddToCartSerializer,
)

from .exceptions import (
    CartItemNotFoundError,
    InvalidQuantityError,
    CartNotActiveError
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


class CartItemDetailView(APIView):
    """
        Handles operations on a single cart item.
        PATCH → update quantity
        DELETE → remove item from cart
    """
    def patch(self, request, item_id):
        try:
            user = request.user
            quantity = request.data.get("quantity")
            
            if quantity is None:
                return Response(
                    {"error": "Quantity is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            updated_item = CartService.update_item_quantity(
                user=user,
                item_id=item_id,
                quantity=int(quantity)
            )
            
            serializer = CartItemSerializer(updated_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except InvalidQuantityError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except CartItemNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except CartNotActiveError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                {"error": "Unable tp update cart item"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    def delete(self, request, item_id):
        try:
            user = request.user
            
            CartService.remove_item_from_cart(
                user=user,
                item_id=item_id
            )
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except CartItemNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except CartNotActiveError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": "Unable to remove cart item"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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