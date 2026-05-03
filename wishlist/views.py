from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .services import WishListService
from .serializers import WishListItemSerializer, ToggleProductSerializer


# Create your views here.
class WishListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        items = WishListService.get_wishlist_items(request.user)
        return Response(WishListItemSerializer(items, many=True).data)
    

"""
    class WishListView(APIView):
        permission_classes = [IsAuthenticated]

        def get(self, request):
            wishlist = WishListService.get_or_create_wishlist(request.user)
            return Response(WishListSerializer(wishlist).data)
"""


class ToggleProductView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ToggleProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = WishListService.toggle_product(
            user=request.user,
            product_id=serializer.validated_data["product_id"],
        )
        
        return Response(result, status=status.HTTP_200_OK)


class RemoveWishListItemView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, product_id):
        result = WishListService.remove_wishlist_item(
            user=request.user,
            product_id=product_id
        )
        
        return Response(result, status=status.HTTP_200_OK)


class MoveToCartView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, product_id):
        result = WishListService.move_to_cart(
            user=request.user,
            product_id=product_id,
        )
            
        return Response(result, status=status.HTTP_200_OK)
        
        
class MoveAllToCartView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        result = WishListService.move_all_to_cart(request.user)
        
        return Response(result, status=status.HTTP_200_OK)

