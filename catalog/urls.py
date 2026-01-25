from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ProductImageViewSet


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')

products_router = routers.NestedDefaultRouter(
    router, r'products', lookup='product'
)

products_router.register(r'images', ProductImageViewSet, basename='product-images')

urlpatterns = router.urls + products_router.urls
