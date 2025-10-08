from django.shortcuts import render, redirect
from store.models import Product
from carts.models import Cart, CartItem
from .models import Order, Payment, OrderProduct
from .forms import OrderForm
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import json

import datetime

def payments(request):
    if request.method == 'POST':
        order_number = request.POST.get('orderID')
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
    payment_method = str(request.POST.get('payment_method')).replace(' ', '-')
    
    payment = Payment(
        user = request.user,
        payment_id = "GENERIC_" + order.order_number,
        payment_method = payment_method,
        amount_paid = order.order_total,
        status = 'Processing',
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variation.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()

        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    CartItem.objects.filter(user=request.user).delete()

    # mail_subject = 'Thank you for your order!'
    # message = render_to_string('orders/order_recieved_email.html', {
    #     'user': request.user,
    #     'order': order,
    # })
    # to_email = request.user.email
    # send_email = EmailMessage(mail_subject, message, to=[to_email])
    # send_email.send()
# 
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }

    return render(request, 'orders/order_complete.html')

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
                'payment_method': request.POST.get('payment_method'),
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')
    
def order_complete(request):
    order_number = request.GET.get('order_number')
    return HttpResponse(order_number)
    transID = request.GET.get('payment_method')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }

        return render(request, 'orders/order_complete.html', context)
    except (Order.DoesNotExist):
        return redirect('home')