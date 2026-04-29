from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewView

router = DefaultRouter()
router.register(r'reviews', ReviewView, basename='reviews')


urlpatterns = [
    path('', include(router.urls)),
]
