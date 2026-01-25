from django.contrib import admin
from .models import Category, Product, ProductImage


models_list = [Category, Product, ProductImage]

# Register your models here.
admin.site.register(models_list)