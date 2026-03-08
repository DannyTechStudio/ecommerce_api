from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_id",
            "product_name",
            "quantity",
            "unit_price",
            "line_total"
        ]
        read_only_fields = tuple(fields)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "status",
            "total_price",
            "currency",
            "created_at",
            "updated_at",
            "paid_at",
            "shipping_full_name",
            "shipping_phone",
            "shipping_street_address",
            "shipping_city",
            "shipping_state",
            "shipping_country",
            "items",
        ]
        read_only_fields = tuple(fields)
        
    def get_item_count(self, obj):
        return obj.items.count()
        

class CompleteOrderSerializer(serializers.Serializer):
    payment_method_id = serializers.UUIDField()
    

class CancelOrderSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False)         
            
