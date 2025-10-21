from django.shortcuts import render,redirect
from carts.models import CartItem
from orders.forms import OrderForm
import datetime

# Create your views here.
def Place_Order(request,total = 0,quantity = 0,tax = 0,grand_total = 0):
    current_user = request.user

    cart_items = CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store')
    
    for item in cart_items:
        total += (item.product.price * item.quantity)   
        quantity += item.quantity
    tax = (2 * total)/100
    grand_total = total + tax

    context = {
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
        'cart_items': cart_items,
        'form' : OrderForm(),
    }
    
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = current_user
            order.order_total = grand_total
            order.tax = tax
            order.ip = request.META.get('REMOTE_ADDR')
            order.save()

            yr = int(datetime.date.today().strftime('%Y'))
            mt = int(datetime.date.today().strftime('%m'))
            dt = int(datetime.date.today().strftime('%d'))

            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")              # coverted to string 
            order.save()                                     # Must save before getting order id
            order_number = current_date + str(order.id)
            order.order_number = order_number
            order.save()
            return redirect('checkout')

        else:
            return redirect('cart')
    else:
        return render (request,'carts/cart.html',context)
    

def Payments(request):
    return render(request,'orders/payment.html')
