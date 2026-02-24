from django.urls import path
from .views import (
    CreateOrderView, 
    OrderDetailView, 
    UserOrdersView
)

urlpatterns = [
    path("create/", CreateOrderView.as_view(), name="create-order"),
    path("", UserOrdersView.as_view(), name="user-orders"),
    path("<uuid:order_id>/", OrderDetailView.as_view(), name="order-detail"),
]

