from .models import Product
from .serializers import ProductReadSerializer
from rest_framework import generics, filters

# Search class
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductReadSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'category']