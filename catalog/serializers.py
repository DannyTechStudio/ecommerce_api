from rest_framework import serializers
from .models import Category, Product


class CategoryReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'updated_at']
    
    
class CategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']
        
    def validate_name(self, name):
        return name.strip()
    
    def validate_slug(self, slug):
        return slug.lower().strip()
    

class ProductReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'category', 'brand', 'price', 'is_active', 'created_at']
      
  
class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'category', 'brand', 'price', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_name(self, name):
        name = name.strip()
        if len(name) < 3:
            raise serializers.ValidationError("Product must be at least 3 characters long.")
        
        return name
    
    
    def validate_slug(self, slug):
        slug = slug.lower().strip()
        qs = Product.objects.filter(slug=slug)
        
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise serializers.ValidationError("A product with this slug already exits")
        
        return slug
    
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must not be negative or zero")
        
        return value
            

    def validate_category(self, category):
        if not category.is_active:
            raise serializers.ValidationError("You cannot assign a product to an inactive category")
        
        return category