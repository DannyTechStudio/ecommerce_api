from rest_framework import viewsets, permissions, status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .models import Category, Product, ProductImage
from .serializers import (
    CategoryReadSerializer, 
    CategoryWriteSerializer,
    ProductReadSerializer,
    ProductWriteSerializer,
    ProductImageReadSerializer,
    ProductImageWriteSerializer
)

from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend



#--------------- Create your views here.
# Category ViewSet
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CategoryReadSerializer
        return CategoryWriteSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {
            "message": "Category created successfully",
            "data": response.data
        }
        return response
        
    def update(self, request, *args, **kwargs):
        response =  super().update(request, *args, **kwargs)
        response.data = {
            "message": "Category updated successfully",
            "data": response.data
        }
        return response
    
    def destory(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return Response({
            "message": "Category deleted successfully"
        }, status=status.HTTP_200_OK)
        
        
# Product ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ProductReadSerializer
        return ProductWriteSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    def create(self, request, *args, **kwargs):
        response =  super().create(request, *args, **kwargs)
        response.data = {
            "message": "Product added successfully",
            "data": response.data
        }
        return response
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.data = {
            "message": "Product updated successfully",
            "data": response.data
        }
        return response
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return Response ({
            "message": "Product removed successfully"
        }, status=status.HTTP_204_NO_CONTENT)


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductReadSerializer
    
    # Enables search and filter together
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # filtering
    filterset_fields = ["category"]
    
    # searching
    search_fields = ["name", "description", "category__name"]
    
    # ordering
    ordering_fields = ["price", "created_at", "name"]
    ordering = ["-created"]     

class ProductImageViewSet(viewsets.ModelViewSet):
    
    def get_queryset(self):
        return (
            ProductImage.objects
            .select_related('product')
            .filter(product_id=self.kwargs['product_pk'])
            .order_by('-created_at')
        )
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['product'] = get_object_or_404(
            Product, pk=self.kwargs['product_pk']
        )
        return context
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ProductImageReadSerializer
        return ProductImageWriteSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    def perform_create(self, serializer):
        image_instance = serializer.save(product=self.get_serializer_context()['product'])
        
        if getattr(image_instance, 'is_primary', False):
            ProductImage.objects.filter(
                product=image_instance.product, is_primary=True
            ).exclude(pk=image_instance.pk).update(is_primary=False)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {
            "message": "Product image added successfully",
            "data": response.data
        }
        return response
    
    def perform_update(self, serializer):
        image_instance = serializer.save()

        if getattr(image_instance, 'is_primary', False):
            ProductImage.objects.filter(
                product=image_instance.product, is_primary=True
            ).exclude(pk=image_instance.pk).update(is_primary=False)
        
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.data = {
            "message": "Image updated successfully",
            "data": response.data
        }
        return response
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return Response({
            "message": "Image removed successfully."
        }, status=status.HTTP_200_OK)