from django.urls import reverse
from django.db import models

import uuid
from categories.models import Category


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='photos/products')
    stock = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if str(self.id) not in self.slug:
            self.slug += str(self.id)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])
