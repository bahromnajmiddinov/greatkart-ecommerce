from django.contrib import admin

from .models import Product, Variation


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'updated', 'is_available',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'category', 'value', 'is_active',)
    list_editable = ('is_active',)
    list_filter = ('product', 'category', 'value', 'is_active',)
