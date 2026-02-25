from django.urls import path
from .views import OrderDetailView, UserOrdersView

urlpatterns = [
    path("", UserOrdersView.as_view(), name="user-orders"),
    path("<uuid:order_id>/", OrderDetailView.as_view(), name="order-detail"),
]

