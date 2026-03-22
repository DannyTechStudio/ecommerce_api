from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    PaymentMethodListView, 
    InitiatePaymentView, 
    VerifyPaymentView, 
    PaymentDetailView,
    PaymentMethodAdminViewset
)

from .webhooks import PayStackWebhookView

router = DefaultRouter()
router.register(r'admin/payment-methods', PaymentMethodAdminViewset, basename='admin-payment-methods')

urlpatterns = [
    path("webhook/", PayStackWebhookView.as_view(), name="webhook"),
    path("methods/", PaymentMethodListView.as_view()),
    path("initiate/", InitiatePaymentView.as_view()),
    path("verify/", VerifyPaymentView.as_view()),
    path("<str:reference>/", PaymentDetailView.as_view()),
]

urlpatterns += router.urls
