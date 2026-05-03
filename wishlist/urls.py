from django.urls import path
from .views import (
    WishListView, 
    ToggleProductView, 
    RemoveWishListItemView, 
    MoveToCartView, 
    MoveAllToCartView
)


urlpatterns = [
    path("", WishListView.as_view(), name='wishlist-detail'),
    path("toggle/", ToggleProductView.as_view(), name="wishlist-toggle"),
    path("remove/<uuid:product_id>/", RemoveWishListItemView.as_view(), name="wishlist-remove"),
    path("move-to-cart/<uuid:product_id>/", MoveToCartView.as_view(), name="wishlist-move-to-cart"),
    path("move-all-to-cart/", MoveAllToCartView.as_view(), name="wishlist-move-all"),
]

