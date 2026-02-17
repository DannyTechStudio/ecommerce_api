from django.urls import path
from .admin_views import (
    AdminCartListView,
    AdminCartDetailView,
    AdminExpireCartView,
    AdminReleaseCartReservationView,
)


urlpatterns = [
    path("carts/", AdminCartListView.as_view()),
    path("carts/<uuid:cart_id>/", AdminCartDetailView.as_view()),
    path("carts/<uuid:cart_id>/expire/", AdminExpireCartView.as_view()),
    path("carts/<uuid:cart_is>/release-reservations/", AdminReleaseCartReservationView.as_view()),
]