from django.db import models
from django.utils import timezone

import uuid
from django_countries.fields import CountryField

from accounts.models import Account
from store.models import Product, Variation


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('PAI', 'Paid'),
        ('UNP', 'Unpaid'),
        ('REF', 'Refunded'),
        ('CAN', 'Cancelled')
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('CC', 'Credit Card'),
        ('PP', 'PayPal'),
    )
    
    payment_id = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=2, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=3, choices=PAYMENT_STATUS_CHOICES, default='UNP')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Payment #{self.payment_id}'


class Address(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = CountryField()
    
    def __str__(self):
        return f'{self.user.username} - {self.address_line1}'


class ContactInfo(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True)
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('PEN', 'Pending'),
        ('SHI', 'Shipped'),
        ('DEL', 'Delivered'),
        ('CAN', 'Cancelled'),
        ('REF', 'Refunded'),
        ('RET', 'Returned'),
    )
    
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=100, unique=True, editable=False)
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=3, choices=ORDER_STATUS_CHOICES, default='PEN')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    
    def __str__(self):
        return f'Order #{self.order_number}'
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        # Generate a unique order number
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        unique_id = uuid.uuid4().hex[:6].upper()  # 6-character unique part
        return f'ORD-{timestamp}-{unique_id}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    variations = models.ManyToManyField(Variation)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.product.name} - Order #{self.order.order_number}'

    @property
    def total(self):
        return self.price * self.quantity
