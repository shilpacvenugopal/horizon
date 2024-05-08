from django.db import models
from dashboard.models import BaseModel
from django.conf import settings
import os
import uuid

# Category Model
class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

def product_image_path(instance, filename):
    return os.path.join('product_images', filename)

# Product Model

class Product(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=product_image_path)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
