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
    path("methods/", PaymentMethodListView.as_view()),
    path("initiate/", InitiatePaymentView.as_view()),
    path("verify/", VerifyPaymentView.as_view()),
    path("<str:reference>/", PaymentDetailView.as_view()),
    path("webhook/", PayStackWebhookView.as_view(), name="webhook"),
]

urlpatterns += router.urls
