from rest_framework.routers import DefaultRouter
from .views import (
    InventoryItemViewSet,
    InventoryReservationViewSet,
    InventoryMovementViewSet
)


router = DefaultRouter()
router.register(r"inventory", InventoryItemViewSet) 
router.register(r"reseravtions", InventoryReservationViewSet) 
router.register(r"movements", InventoryMovementViewSet)

urlpatterns = router.urls
