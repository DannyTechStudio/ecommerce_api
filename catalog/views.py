from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Category, Product
from .serializers import (
    CategoryReadSerializer, 
    CategoryWriteSerializer,
    ProductReadSerializer,
    ProductWriteSerializer
)


# Create your views here.
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
        }, status=status.HTTP_204_NO_CONTENT)
        
        

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