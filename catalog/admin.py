from django.contrib import admin
from .models import Category, Product


models_list = [Category, Product]

# Register your models here.
admin.site.register(models_list)