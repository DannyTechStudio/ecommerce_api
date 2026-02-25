from rest_framework import serializers
from .models import Cart, CartItem

from order.serializers import OrderSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    price = serializers.DecimalField(source="price_snapshot", max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            "id",
            "product_id",
            "product_name",
            "price",
            "quantity",
        ]
        
        
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            "id",
            "status",
            "expires_at",
            "items",
        ]


class AddToCartSerializer(serializers.Serializer): 
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    

class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
    

class CheckoutResponseSerializer(serializers.Serializer):
    order = OrderSerializer()
    checked_out_cart_id = serializers.UUIDField(source="checked_out_cart.id") 
    new_active_cart_id = serializers.UUIDField(source="active_cart.id") 
    message = serializers.SerializerMethodField()
     
    def get_message(self, obj): 
        return "Checkout successful"