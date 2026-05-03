import uuid
from django.db import models
from django.conf import settings

from catalog.models import Product

User = settings.AUTH_USER_MODEL


# Create your models here.
class WishList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wishlist")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.id} - {self.user}"
    
    
class WishListItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    wishlist = models.ForeignKey(WishList, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlist_items")
    added_at = models.DateTimeField(auto_now_add=True)
    
    constraints = [
        models.UniqueConstraint(
            fields=["wishlist", "product"],
            name="unique_product_per_wishlist"
        )
    ]
    
    def __str__(self):
        return f"{self.wishlist} - {self.product}"

