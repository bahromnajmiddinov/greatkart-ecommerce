from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from store.models import Product, Variation
from .models import Cart, CartItem


@receiver(user_logged_in)
def move_session_data_to_database(sender, request, user, **kwargs):
    # Get session data
    session_cart = request.session('cart', {})
    
    # Iterate through the session data and save to database
    for key, value in session_cart.items():
        # cart = {
        #     ['product_id', ['variation_color', 'variation_size']]: [quantity, cart_item_id],
        # }
        try:
            product = Product.objects.get(id=key[0])
            cart, created = Cart.objects.get_or_create(cart_id=user.id)
            cart_item = CartItem.objects.get_or_create(product=product, cart=cart)
            variations = []
            
            try:
                variation_color = Variation.objects.get(id=key.split(' ')[1], category='color')
                variation_size = Variation.objects.get(id=key.split(' ')[2], category='size')
                variations.append(variation_color)
                variations.append(variation_size)
            except: pass
            if not cart_item.filter(variations_in=variations).exists():
                cart_item.variations.add(variations)
            cart_item.quantity = value[0]
        except: pass
    
    if session_cart:
        del request.session['cart']   
        