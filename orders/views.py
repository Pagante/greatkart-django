from time import strftime
from orders.models import Order
from django.shortcuts import redirect, render
from django.http import HttpResponse, response, JsonResponse
from cart.models import CartItem,Cart
from .forms import OrderForm
import datetime
from .models import Order, OrderProduct, Payment
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# Create your views here.

def payments(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    payments = Payment (
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_methods'],
        amount_paid = order.order_total,
        status = body['status']
    )
    payments.save()
    order.payment = payments
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user = request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payments
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product.id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        #Reduce Product Quantity
        product = Product.objects.get(id=item.product.id)
        product.stock -= item.quantity
        product.save()
    
    CartItem.objects.filter(user=request.user).delete()

    mail_subject = 'Thank you for your order.'
    message = render_to_string('orders/order_received_email.html', {
        'user' : request.user,
        'order': order
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject,message, to = [to_email])
    send_email.send()

    data = {
        'order_number': order.order_number,
        'transID': payments.payment_id,
    }
    return response.JsonResponse(data)

def place_order(request, total = 0, quantity = 0):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    tax = 0
    grandtotal = 0

    for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    
    tax = (2 * total)/100
    grandtotal = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grandtotal
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # To generate order ID
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime('%Y%m%d')
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            order = Order.objects.get(user=current_user, is_ordered = False, order_number = order_number)
            context = {
                'order': order,
                'cart_items' : cart_items,
                'total': total,
                'tax': tax,
                'grandtotal' : grandtotal,
            }
            return render(request, 'orders/payments.html', context)
        else:
            return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    try:
        
        order = Order.objects.get(order_number=order_number, is_ordered = True)
        order_product = OrderProduct.objects.filter(order_id = order.id)
        payments = Payment.objects.get(payment_id = transID)

        subtotal = 0
        for i in order_product:
            subtotal += i.product_price * i.quantity

        context = {
            'order': order,
            'order_product': order_product,
            'order_number': order.order_number,
            'transID': payments.payment_id,
            'payments': payments,
            'subtotal' : subtotal,
        }
        return render(request, 'orders/order_complete.html', context)

    except(Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')




    


