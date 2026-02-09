from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone

from .permissions import IsAdminUser, IsReservationOwnerOrAdmin
from .models import InventoryItem, InventoryMovement, InventoryReservation
from .serializers import (
    InventoryItemSerializer, 
    InventoryReservationSerializer, 
    InventoryMovementSerializer
)


# Create your views here.
class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.select_related("product")
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get", "patch"]
    
    
class InventoryReservationViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryReservationSerializer
    permission_classes = [IsReservationOwnerOrAdmin]
    http_method_names = ["get", "post"]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return InventoryReservation.objects.select_related("inventory_item", "customer")
        return InventoryReservation.objects.filter(customer=user).select_related("inventory_item")
    
    def perform_create(self, serializer):
        serializer.save()
        
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        
        if not reservation.is_active:
            return Response(
                {"detail": "Reservation already inactive."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        with transaction.atomic():
            item = InventoryItem.objects.select_for_update().get(
                id=reservation.inventory_item.id
            )
            
            item.release_stock(reservation.quantity)
            
            reservation.is_active = False
            reservation.save()
        return Response({"detail": "Reservation cancelled."})
    

class InventoryMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryMovement.objects.select_related("inventory_item")
    serializer_class = InventoryMovementSerializer
    permission_classes = [IsAdminUser]