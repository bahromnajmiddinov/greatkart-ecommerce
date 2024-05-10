from django.db import models

from store.models import Product
from store.models import Variation


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.product.name
    
    @property
    def total(self):
        return self.quantity * self.product.price
        
