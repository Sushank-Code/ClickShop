from carts.models import Cart,CartItem
from carts.views import _cart_id

def Counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else :
        try:
            cart = Cart.objects.filter(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart[:1])      
            # gettting the first cart Id(Which contain evry product in cart)
            
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count = cart_count)