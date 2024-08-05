from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from carts.models import CartItem
from carts.views import _get_cart
from .models import Product
from categories.models import Category


def store(request):
    category = request.GET.get('category', '')
    page_number = request.GET.get('page', 1)
    search = request.GET.get('search', '')
    
    products = Product.objects.filter(is_available=True)\
        .filter(category__slug__icontains=category)\
        .filter(Q(name__icontains=search) | Q(description__icontains=search))
    paginator = Paginator(products, 1)
    paged_products = paginator.get_page(page_number)
    products_count = products.count()
    categories = Category.objects.all()
    
    context = {
        'products': paged_products,
        'products_count': products_count,
        'categories': categories,
        'search': search,
    }
    
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    product = get_object_or_404(Product, slug=product_slug, category__slug=category_slug)
    
    colors = product.variation_set.colors
    sizes = product.variation_set.sizes
    
    context = {
        'product': product,
        'colors': colors,
        'sizes': sizes,
    }
    
    return render(request, 'store/product_detail.html', context)
