from rest_framework import serializers
from .models import WishList, WishListItem


class WishListItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    
    class Meta:
        model = WishListItem
        fields = [
            "id",
            "product_id",
            "product_name",
        ]


class WishListSerializer(serializers.ModelSerializer):
    items = WishListItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = WishList
        fields = [
            "id",
            "items"
        ]
        
class BaseProductSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
        
        
class ToggleProductSerializer(BaseProductSerializer):
    pass


class RemoveWishListItemSerializer(BaseProductSerializer):
    pass


class MoveToCartSerializer(BaseProductSerializer):
    pass


class MoveAllToCartSerializer(serializers.Serializer):
    pass
