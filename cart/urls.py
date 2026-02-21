from django.urls import path
from .views import (
    CartView,
    AddToCartView,
    UpdateCartItemView,
    RemoveCartItemView,
    CheckoutView,
)

urlpatterns = [
    path("", CartView.as_view(), name="cart-detail"),
    path("add/", AddToCartView.as_view(), name="cart-add"),
    path("items/<int:item_id>/", UpdateCartItemView.as_view(), name="cart-item-update"),
    path("items/<int:item_id>/remove/", RemoveCartItemView.as_view(), name="cart-item-remove"),
    path("checkout/", CheckoutView.as_view(), name="cart-checkout"),
]
