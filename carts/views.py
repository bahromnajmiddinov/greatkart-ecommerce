from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required

import shortuuid

from store.models import Product, Variation
from .models import Cart, CartItem


def _get_cart(request):
    if request.user.is_anonymous:
        cart = request.session.get('cart', {})
    else:
        cart = Cart.objects.get_or_create(cart_id=request.user.id)
        
    return cart


def _get_variation(product, color, size):
    variations = []
    try:
        variation_color = Variation.objects.get(product=product, value__iexact=color, category='color')
        variation_size = Variation.objects.get(product=product, value__iexact=size, category='size')
        variations.append(variation_color)
        variations.append(variation_size)
    except: pass
    
    return variations


@require_POST
def add_cart(request, product_id):
    color = request.POST.get('color', '')
    size = request.POST.get('size', '')
    product = get_object_or_404(Product, pk=product_id)
    variations = _get_variation(product, color, size)
    
    cart = _get_cart(request)
    # anonymous user cart item addition
    if request.user.is_anonymous:
        # cart = {
        #     ['product_id', ['variation_color', 'variation_size']]: [quantity, cart_item_id],
        # }
        variations = [variations[0].id, variations[1].id]
        
        if ['product_id', variations] not in cart:
            cart[['product_id', variations]] = [1, shortuuid.uuid()]
        else:
            cart[['product_id', variations]][0] += 1
        request.session['cart'] = cart
        return redirect('cart')
    # authorized user cart item addition
    cart_item = CartItem.objects.filter(product=product, cart=cart).filter(variations__in=variations).first()
    
    if not cart_item:
        cart_item = CartItem.objects.create(product=product, cart=cart)
        cart_item.variations.add(*variations)

    cart_item.quantity += 1
    cart_item.save()
    
    return redirect('cart')


@require_POST
def increase_cart_item(request, cart_item_id):
    # anonymous user cart item increase
    if request.user.is_anonymous:
        cart = _get_cart(request)
        for key, value in cart.items():
            if value[1] == cart_item_id:
                product = get_object_or_404(Product, pk=key[0])
                if product.stock > value[0]:
                    cart[key][0] += 1
                break
        request.session['cart'] = cart
        return redirect('cart')
    # authorized user cart item increase
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    if cart_item.product.stock > cart_item.quantity:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('cart')


@require_POST
def remove_from_cart(request, cart_item_id):
    # anonymous user cart removal
    if request.user.is_anonymous:
        cart = _get_cart(request)
        for key, value in cart.items():
            if value[1] == cart_item_id:
                if value[0] > 1:
                    cart[key][0] -= 1
                del cart[key]
                break
        request.session['cart'] = cart
        return redirect('cart')
    # authorized user cart removal
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect('cart')


@require_POST
def delete_from_cart(request, cart_item_id):
    # anony user cart removal
    if request.user.is_anonymous:
        cart = _get_cart(request)
        for key in cart.keys():
            if key[1] == cart_item_id:
                del cart[key]
                break
        request.session['cart'] = cart
        return redirect('cart')
    # authorized user cart removal
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    cart_item.delete()
    
    return redirect('cart')


def cart(request):
    cart = _get_cart(request)
    total = 0
    quantity = 0
    if request.user.is_anonymous:
        cart_items = []
        for key, value in cart.items():
            product = get_object_or_404(Product, pk=key[0])
            total += product.price * value[0]
            quantity += value[0]
            
            cart_items.append({
                'product': product,
                'quantity': value[0],
                'id': value[1],
            })
    else:    
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += cart_item.total
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


@login_required(login_url='login')
def checkout(request):
    cart= _get_cart(request)
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    cart_items.annotate(total_price=F('product__price') * F('quantity'))
    total = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
    tax = (2 * total) / 100
    grand_total = total + tax
    context = {
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/place-order.html', context)
