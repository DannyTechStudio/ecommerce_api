from rest_framework import serializers
from .models import Review

from order.models import Order, OrderItem, OrderStatus

# Review serializer
class ReviewSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        min_value=1,
        max_value=5,
        error_messages={
            "min_value": "Rating must be between 1 and 5",
            "max_value": "Rating must be between 1 and 5",
        }
    )
    
    class Meta:
        model = Review
        fields = ["id", "user", "product", "rating", "comment", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "status", "created_at", "updated_at"]
        
    def validate(self, data):
        rating = data.get("rating")
        comment = data.get("comment")
        product = data.get("product")
        user = self.context["request"].user
        
        has_purchased = OrderItem.objects.filter(
            order__user=user,
            order__status=OrderStatus.DELIVERED,
            product_id=product.id
        ).exists()
        
        if rating is not None and rating <= 3 and not (comment or "").strip():
            raise serializers.ValidationError({
                "comment": "Your feedback helps us improve. Please provide a brief comment."
            })
        
        if not has_purchased:
            raise serializers.ValidationError({
                "product": "You can only review products you have purchased and received."
            })  
            
        return data
    
    