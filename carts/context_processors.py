from .models import CartItem
from .views import _get_cart


def cart_item_counter(request):
    cart = _get_cart(request)
    if not request.user.is_anonymous:
        cart_items_count = CartItem.objects.filter(cart=cart).count()
    else:
        cart_items_count = len(cart)
    
    return dict(cart_items_count=cart_items_count)
