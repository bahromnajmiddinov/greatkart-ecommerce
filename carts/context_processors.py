from .models import Cart, CartItem
from .views import _cart_id


def cart_item_counter(request):
    cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))
    cart_items_count = CartItem.objects.filter(cart=cart).count()
    
    return dict(cart_items_count=cart_items_count)
