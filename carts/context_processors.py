from .models import CartItem
from .views import _get_cart


def cart_item_counter(request):
    cart = _get_cart(request)
    if request.user.is_authenticated:
        cart_items_count = CartItem.objects.filter(cart=cart).count()
    else:
        cart_items_count = len(cart)
    
    return dict(cart_items_count=cart_items_count)
