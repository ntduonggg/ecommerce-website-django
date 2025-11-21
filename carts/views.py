from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
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

def _get_cart_context(cart_items):
    total = 0
    quantity = 0
    tax = 0
    discount = 0
    discount_percent = 0
    grand_total = 0
    
    for cart_item in cart_items:
        total += float(cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    
    tax = (2 * total) / 100
    
    if total <= 10000000:
        discount_percent = 0.05
    elif total <= 50000000:
        discount_percent = 0.07
    else:
        discount_percent = 0.1
    
    discount = total * discount_percent
    grand_total = total + tax - discount
    
    return {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'discount': discount,
        'discount_percent': discount_percent * 100,
        'grand_total': grand_total
    }

def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    if current_user.is_authenticated:
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
            cart.save()
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

    if is_cart_item_exists:
        if current_user.is_authenticated:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
        else:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
        
        id = []
        exist_products_list = []
        for item in cart_item:
            exist_products_list.append(item.product)
            id.append(item.id)
        
        if product in exist_products_list:
            index = exist_products_list.index(product)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            if current_user.is_authenticated:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            item.save()

    else:
        if current_user.is_authenticated:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
        cart_item.save()

    return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
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
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        cart_item.delete()
    except:
        pass
    return redirect('cart')

def cart(request):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        context = _get_cart_context(cart_items)
    except ObjectDoesNotExist:
        context = _get_cart_context([])
    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        context = _get_cart_context(cart_items)
    except ObjectDoesNotExist:
        context = _get_cart_context([])
    return render(request, 'store/checkout.html', context)