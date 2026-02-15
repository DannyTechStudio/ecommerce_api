from rest_framework import serializers
from .models import Cart, CartItem

"""
    Cart Output Serializers
"""
class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    
    
    class Meta:
        model = CartItem
        field = ["id", "product_id", "product_name", "quantity", "price_snapshot", "created_at"]
        

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ["id", "status", "expires_at", "created_at", "updated_at", "is_active", "total_items", "items"]
        
    def get_total_items(self, obj):
        return obj.items.count()
    
    def get_is_active(self, obj):
        return obj.is_active()
    

"""
    Cart Input Serializers
"""
class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)
    

class UpdateCartItemSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=0)
    

class RemoveCartItemSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()