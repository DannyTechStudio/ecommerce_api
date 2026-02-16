from django.urls import path
from .views import (
    CartView, 
    AddToCartView,
    CartItemDetailView,
    CheckoutCartView
)

urlpatterns = [
    path("", CartView.as_view(), name="cart-detail"),
    path("items/", AddToCartView.as_view(), name="cart-add-item"),
    path("items/<uuid:item_id>/", CartItemDetailView.as_view(), name="cart-item-detail"),
    path("checkout/", CheckoutCartView.as_view(), name="cart-checkout"),
]

