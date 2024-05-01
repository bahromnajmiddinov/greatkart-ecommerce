from django.shortcuts import render, get_object_or_404

from .models import Product
from categories.models import Category


def store(request):
    category = request.GET.get('category', '')
    
    products = Product.objects.filter(is_available=True).filter(category__slug__icontains=category)
    products_count = products.count()
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'products_count': products_count,
        'categories': categories,
    }
    
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    product = get_object_or_404(Product, slug=product_slug, category__slug=category_slug)
    
    context = {
        'product': product,
    }
    
    return render(request, 'store/product_detail.html', context)
