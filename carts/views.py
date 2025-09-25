from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from . import views
from django.contrib.auth.decorators import login_required

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variations = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]

            try:
                variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
                product_variations.append(variation)
            except:
                pass

    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
        cart.save()

    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        id = []
        exist_variations_list = []
        for item in cart_item:
            existing_variations = item.variation.all()
            exist_variations_list.append(list(existing_variations))
            id.append(item.id)

        if product_variations in exist_variations_list:
            index = exist_variations_list.index(product_variations)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variations) > 0:
                item.variation.clear()
                item.variation.add(*product_variations)
            item.save()
    else:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart
        )
        if len(product_variations) > 0:
            cart_item.variation.clear()
            cart_item.variation.add(*product_variations)
        cart_item.save()

    return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        cart_item.delete()
    except:
        pass
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    discount = 0
    discount_percent = 0
    grand_total = 0
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += float(cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        if total <= 10000000:
            discount_percent = 0.05
        elif total <= 50000000:
            discount_percent = 0.07
        else:
            discount_percent = 0.1
        discount = total * discount_percent
        grand_total = total + tax - discount
        
    except Cart.DoesNotExist:
        pass
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'discount': discount,
        'discount_percent': discount_percent * 100,
        'grand_total': grand_total
    }
    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    tax = 0
    discount = 0
    discount_percent = 0
    grand_total = 0
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += float(cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        if total <= 10000000:
            discount_percent = 0.05
        elif total <= 50000000:
            discount_percent = 0.07
        else:
            discount_percent = 0.1
        discount = total * discount_percent
        grand_total = total + tax - discount
        
    except Cart.DoesNotExist:
        pass
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'discount': discount,
        'discount_percent': discount_percent * 100,
        'grand_total': grand_total
    }
    return render(request, 'store/checkout.html', context)