from django.shortcuts import render, redirect
from carts.models import Cart, CartItem
from .models import Order
from .forms import OrderForm
from django.http import HttpResponse

import datetime

def payments(request):
    return render(request, 'orders/payments.html')

def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count < 0:
        return redirect('store')

    tax = 0
    discount = 0
    discount_percent = 0
    grand_total = 0
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

    if request.method == 'POST':
        form = OrderForm(request.POST)
        # return HttpResponse(form.errors)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone_number = form.cleaned_data['phone_number']
            data.address_line1 = form.cleaned_data['address_line1']
            # data.address_line2 = form.cleaned_data['address_line2']
            data.province = form.cleaned_data['province']
            data.village = form.cleaned_data['village']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.discount = discount
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            yr = int(datetime.date.today().strftime('%Y'))
            mt = int(datetime.date.today().strftime('%m'))
            dt = int(datetime.date.today().strftime('%d'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime('%Y%m%d')
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'grand_total': grand_total,
                'tax': tax,
                'discount': discount,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')