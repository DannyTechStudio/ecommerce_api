from rest_framework import serializers

from .models import (
    Order,
    OrderItem
)


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
    
    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "status",
            "total_price",
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
            
            
