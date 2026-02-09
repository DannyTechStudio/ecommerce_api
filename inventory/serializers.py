from django.db import transaction
from rest_framework import serializers
from .models import InventoryItem, InventoryReservation, InventoryMovement
from django.utils import timezone


# Serializers
class InventoryItemSerializer(serializers.ModelSerializer):
    available_quantity = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryItem
        fields = ['id', 'product', 'quantity_on_hand', 'quantity_reserved', 'available_quantity', 'created_at']
        read_only_fields = ['id', 'product', 'quantity_reserved', 'available_quantity', 'created_at']

    def get_available_quantity(self, obj):
        return obj.available_quantity()
    
    def validate_quantity_on_hand(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        return value
    
    def update(self, instance, validated_data):
        request = self.context.get("request")
        
        if not request or not request.user.is_staff:
            raise serializers.ValidationError("Only admin user can update inventory stock")
        
        old_stock_quantity = instance.quantity_on_hand
        new_stock_quantity = validated_data.get("quantity_on_hand", old_stock_quantity)
        
        if new_stock_quantity > old_stock_quantity:
            restock_quantity = new_stock_quantity - old_stock_quantity
            
            InventoryMovement.objects.create(
                inventory_item=instance,
                quantity=restock_quantity,
                movement_type="RESTOCK",
                reference="admin_restock"
            )
            
        instance.quantity_on_hand = new_stock_quantity
        instance.save()
        return instance


class InventoryReservationSerializer(serializers.ModelSerializer):
    has_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryReservation
        fields = ['id', 'inventory_item', 'customer', 'quantity', 'created_at', 'expires_at', 'is_active', 'has_expired']
        read_only_fields = ['id', 'customer', 'created_at', 'is_active', 'has_expired']
        
    def get_has_expired(self, obj):
        return obj.has_expired()
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero")
        return value
    
    def validate(self, attrs):
        inventory_item = attrs.get("inventory_item")
        quantity = attrs.get("quantity")

        if quantity > inventory_item.available_quantity():
            raise serializers.ValidationError("Insufficient stock available for reservation")
        
        return attrs
    
    def create(self, validated_data):
        request = self.context["request"]
        inventory_item = validated_data["inventory_item"]
        quantity = validated_data["quantity"]
        
        with transaction.atomic():
            inventory_item = (
                InventoryItem.objects
                .select_for_update()
                .get(id=validated_data["inventory_item"].id)
            )
            
            if quantity > inventory_item.available_quantity():
                raise serializers.ValidationError("Insufficient stock available for reservation.")
            
            inventory_item.reserve_stock(quantity)
            
            reservation = InventoryReservation.objects.create(
                inventory_item=inventory_item,
                customer=request.user,
                quantity=quantity,
                expires_at=timezone.now() + timezone.timedelta(hours=24)
            )

        return reservation


class InventoryMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryMovement
        fields = ['id', 'inventory_item', 'quantity', 'movement_type', 'reference', 'created_at']
        read_only_fields = fields
        
