from django import template

from carts.models import CartItem
from carts.views import _get_cart


register = template.Library()


@register.filter
def is_in_cart(product, request):
    try:
        return CartItem.objects.filter(product=product, cart__cart_id=_get_cart(request)).exists()
    except:
        return False
