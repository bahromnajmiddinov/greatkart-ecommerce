from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from carts.views import _get_cart, CartItem
from .models import Order, OrderItem
from .forms import AddressForm, ContactInfoForm


@login_required
def checkout(request):
    login_url = reverse('login') + '?next=cart'
    
    total = 0
    
    address_form = AddressForm()
    contact_info_form = ContactInfoForm()
    
    cart = _get_cart(request)
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    
    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        contact_info_form = ContactInfoForm(request.POST)
        
        if address_form.is_valid() and contact_info_form.is_valid():
            address = address_form.save(user=request.user)
            contact_info_form.save(address=address)
            order = Order.objects.create(user=request.user, address=address)
            
            for item in cart_items:
                OrderItem.objects.create(order=order, product=item.product,
                                         price=item.product.price, quantity=item.quantity,
                                         variations=item.variations)
                total += item.total
            
            order.total_amount = total
            order.save()
            
            # Clear the cart
            cart.clear()
            return redirect('store:checkout-success')
    
    for cart_item in cart_items:
        total += cart_item.total
    tax = (2 * total) / 100
    grand_total = total + tax
    context = {
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
        'address_form': address_form,
        'contact_info_form': contact_info_form,
    }
    return render(request, 'store/place-order.html', context)


def order_complete(request):
    return render(request, 'store/order_complete.html')
