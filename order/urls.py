from django.urls import path
from .views import (
    UserOrdersView, 
    OrderDetailView, 
    CompleteOrderSerializer, 
    CancelOrderView,
    ShipOrderView,
    DeliverOrderView,
)

urlpatterns = [
    path("", UserOrdersView.as_view(), name="user-orders"),
    path("<uuid:order_id>/", OrderDetailView.as_view(), name="order-detail"),
    path("<uuid:order_id>/complete/", CompleteOrderSerializer.as_view(), name="complete-order"),
    path("<uuid:order_id>/cancel/", CancelOrderView.as_view(), name="cancel-order"),
    path("<uuid:order_id>/ship/", ShipOrderView.as_view(), name="ship-order"),
    path("<uuid:order_id>/deliver/", DeliverOrderView.as_view(), name="deliver-order"),
]

