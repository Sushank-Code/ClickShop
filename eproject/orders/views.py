from django.shortcuts import render,redirect
from carts.models import CartItem
from orders.models import Order
from orders.forms import OrderForm

# Order_number
import datetime

# payment gateway(Esewa)
import uuid,hmac,hashlib,base64


# Create your views here.

def Place_Order(request,total = 0,tax = 0,grand_total = 0):

    current_user = request.user

    cart_items = CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store')
    
    for item in cart_items:
        total += (item.product.price * item.quantity)   
    
    tax = (2 * total)/100
    grand_total = total + tax
  
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

            request.session['allow_payment'] = True        
        
            payment_option = order.payment_option
            
            if payment_option == 'esewa':
                return redirect('esewa_payment',order_number=order.order_number)
            
            elif payment_option == 'khalti':
                return redirect('khalti_payment',order_number=order.order_number)
            
            elif payment_option == 'cod':
                return redirect('cod_payment',order_number = order.order_number)
            
        else:
            return redirect('cart')
    else:
        return render (request,'carts/cart.html')

def generate_signature(total_amount,transaction_uuid,product_code,secret_key):
    # core content of transaction
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"

    # generating signature
    signature = hmac.new(
        bytes(secret_key,'utf-8'),
        msg=bytes(message,'utf-8'),
        digestmod=hashlib.sha256        
    ).digest()

    signature_base64 = base64.b64encode(signature).decode()

    return signature_base64 

def eSewa_payment(request,order_number,total = 0,tax = 0,grand_total = 0):

    if not request.session.get('allow_payment'):
        return redirect('cart')
    
    current_user = request.user
    order = Order.objects.get(user = current_user , is_ordered = False,order_number=order_number)

    cart_items = CartItem.objects.filter(user = current_user)
   
    for item in cart_items:
        total += (item.product.price * item.quantity)   
    tax = (2 * total)/100
    grand_total = total + tax

    transaction_uuid = str(uuid.uuid4())            # generate uuid
    secret_key = "8gBm/:&EnhH.1/q"
    product_code = "EPAYTEST"

    signature = generate_signature(grand_total, transaction_uuid, product_code, secret_key)

    context = {
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
        'cart_items': cart_items,
        'order' : order,
        'transaction_uuid' : transaction_uuid,
        'product_code' : product_code,                                        # test product_code
        'signed_field_name': "total_amount,transaction_uuid,product_code",
        'signature': signature,
        'esewa_url':'https://rc-epay.esewa.com.np/api/epay/main/v2/form' ,     # test url
        'success_url': "http://127.0.0.1:8000/orders/payment_success",                            
        'failure_url': "http://127.0.0.1:8000/orders/payment_failure",                       
    }
    return render(request, 'orders/payment.html',context) 

def Khalti_payment(request):
    pass

def COD_payment(request):
    pass

def Payment_Success(request):
    print(request.session.get('allow_payment'))
    if not request.session.get('allow_payment'):
        return redirect('cart')

    request.session.pop('allow_payment', None)
    return render(request,'orders/payment_success.html')

def Payment_Failure(request):
    if not request.session.get('allow_payment'):
        return redirect('cart')

    request.session.pop('allow_payment', None)
    return render(request,'orders/payment_failure.html')