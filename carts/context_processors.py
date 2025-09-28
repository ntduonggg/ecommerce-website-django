from carts.models import Cart, CartItem
from carts.views import _cart_id


def counter(request):
    count_cart_items = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart_items = CartItem.objects.all().filter(cart=cart[:1])

            for cart_item in cart_items:
                count_cart_items += cart_item.quantity
        except Cart.DoesNotExist:
            count_cart_items = 0
    return dict(count_cart_items=count_cart_items)    