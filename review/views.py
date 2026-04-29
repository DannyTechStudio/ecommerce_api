from rest_framework import viewsets
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from .models import Review, ReviewStatus
from .serializers import ReviewSerializer
from .permissions import IsOwner

# Create your views here.
class ReviewView(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    
    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Review.objects.filter(
            Q(status=ReviewStatus.APPROVED) | Q(user=self.request.user)
        )
        
        product_id = self.request.query_params.get("product")
        if product_id:
            queryset = queryset.filter(product_id=product_id)
            
        return queryset.select_related("user", "product")
    
    def perform_create(self, serializer):
        user = self.request.user
        product = serializer.validated_data["product"]
        
        if Review.objects.filter(user=user, product=product).exists():
            raise ValidationError("You have already reviewed this product.")
        
        serializer.save(user=user)

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status == ReviewStatus.REJECTED:
            instance.status = ReviewStatus.PENDING
            instance.save()

    def perform_destroy(self, instance):
        instance.delete()