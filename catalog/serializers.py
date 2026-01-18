from rest_framework import serializers
from .models import Category


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