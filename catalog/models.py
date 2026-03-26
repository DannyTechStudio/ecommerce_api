import uuid
from django.db import models, transaction


# Create your models here.
class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
# Product Model
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    quantity = models.PositiveIntegerField()
    brand = models.CharField(max_length=150, blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category__name', 'name']
    
    # Ensures 'is_active' is 'False' when quantity is zero
    def save(self, *args, **kwargs):
        self.is_active = self.quantity > 0
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


# Product Image Model
class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    
    def product_image_path(instance, filename):
        return f'products/{instance.product.id}/{filename}'
    
    image = models.ImageField(upload_to=product_image_path)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product'], condition=models.Q(is_primary=True), name='unique_primary_image_per_product')
        ]

    def delete(self, *args, **kwargs):
        previous_primary_image = self.is_primary
        product = self.product
        
        with transaction.atomic():
            super().delete(*args, **kwargs)
            
            if previous_primary_image:
                next_primary_image = ProductImage.objects.filter(product=product).order_by('created_at').first()
                
                if next_primary_image:
                    next_primary_image.is_primary = True
                    next_primary_image.save(update_fields=['is_primary'])

    def __str__(self):
        return f"Image for {self.product.name}"


