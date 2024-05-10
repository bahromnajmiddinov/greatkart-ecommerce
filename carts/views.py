from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.db.models import Q

from store.models import Product, Variation
from .models import Cart, CartItem


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        request.session.create()
        cart = request.session.session_key
    return cart


@require_POST
def add_cart(request, product_id):
    color = request.POST.get('color', '')
    size = request.POST.get('size', '')
    product = get_object_or_404(Product, pk=product_id)
    variations = []
    try:
        variation_color = Variation.objects.get(product=product, value__iexact=color, category='color')
        variation_size = Variation.objects.get(product=product, value__iexact=size, category='size')
        variations.append(variation_color)
        variations.append(variation_size)
    except:
        pass
    
    cart, cart_created = Cart.objects.get_or_create(cart_id=_cart_id(request))
    cart_item = CartItem.objects.filter(product=product, cart=cart).filter(variations__in=variations).first()
    
    if not cart_item:
        cart_item = CartItem.objects.create(product=product, cart=cart)
        cart_item.variations.add(*variations)

    cart_item.quantity += 1
    cart_item.save()
    
    return redirect('cart')


@require_POST
def increase_cart(request, cart_id):
    cart_item = CartItem.objects.get(pk=cart_id)
    if cart_item.product.stock > cart_item.quantity:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('cart')


@require_POST
def remove_cart(request, cart_id):
    cart_item = CartItem.objects.get(pk=cart_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect('cart')


@require_POST
def delete_cart(request, cart_id):
    cart_item = CartItem.objects.get(pk=cart_id)
    cart_item.delete()
    
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    cart, cart_created = Cart.objects.get_or_create(cart_id=_cart_id(request))
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    total = 0
    quantity = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax
    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)
