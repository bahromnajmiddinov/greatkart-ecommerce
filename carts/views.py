from django.shortcuts import render, redirect, get_object_or_404

from store.models import Product
from .models import Cart, CartItem


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        request.session.create()
        cart = request.session.session_key
    return cart


def add_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart, cart_created = Cart.objects.get_or_create(cart_id=_cart_id(request))
    cart_item, cart_item_created = CartItem.objects.get_or_create(product=product, cart=cart)
    cart_item.quantity += 1
    cart_item.save()
    
    return redirect('cart')


def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, pk=product_id)
    cart_item = CartItem.objects.get(cart=cart, product=product)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect('cart')


def delete_cart(request, product_id):
    cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))
    product = get_object_or_404(Product, pk=product_id)
    cart_item = CartItem.objects.get(cart=cart, product=product)
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
