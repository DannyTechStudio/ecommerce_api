from django.urls import path
from .views import (
    PaymentMethodListView, 
    InitiatePaymentView, 
    VerifyPaymentView, 
    PaymentDetailView
)

from .webhooks import PayStackWebhookView

urlpatterns = [
    path("methods/", PaymentMethodListView.as_view()),
    path("initiate/", InitiatePaymentView.as_view()),
    path("verify/", VerifyPaymentView.as_view()),
    path("<str:reference>/", PaymentDetailView.as_view()),
    path("webhook/paystack/", PayStackWebhookView.as_view(), name="paystack-webhook"),
]
