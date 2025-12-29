from django.shortcuts import render,redirect,HttpResponse
from carts.models import CartItem
from orders.models import Order,Payment
from orders.forms import OrderForm

# Order_number
import datetime,random,string

# payment gateway(Esewa)
import uuid,hmac,hashlib,base64,json,requests

from django.conf import settings
 
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
            request.session['pending_order_number'] = order.order_number      
        
            payment_option = order.payment_option
            
            if payment_option == 'esewa':
                return redirect('esewa_payment',order_number=order.order_number)
            
            elif payment_option == 'khalti':
                return redirect('khalti_payment',order_number=order.order_number)
            
            else:
                return redirect('cod_payment',order_number = order.order_number)
        else:
            return redirect('cart')
    else:
        return render (request,'carts/cart.html')

# E-sewa Signature 
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
    secret_key = settings.ESEWA_SECRET_KEY
    product_code = settings.ESEWA_PRODUCT_CODE

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
        'esewa_url':settings.ESEWA_PAYMENT_URL ,                             # test url
        'success_url': "http://127.0.0.1:8000/orders/payment_success",                            
        'failure_url': "http://127.0.0.1:8000/orders/payment_failure",                       
    }
    return render(request, 'orders/payment.html',context) 

def verify_esewa_payment(request,data_encoded,order_number):

    try:
        decoded_bytes = base64.b64decode(data_encoded)       # base64 text to raw bytes
        decoded_str = decoded_bytes.decode('utf-8')          # bytes to string
        payment_info = json.loads(decoded_str)               # string with json text to python dictionary

        transaction_uuid = payment_info.get("transaction_uuid")         # accessing dictionary
        product_code = payment_info.get("product_code")
        total_amount = payment_info.get("total_amount")

        verify_url = settings.ESEWA_VERIFY_URL
        payload = {
            "product_code": product_code,
            "total_amount": total_amount,
            "transaction_uuid": transaction_uuid,
        }

        response = requests.get(verify_url, params=payload)   # Esewa does get (not post)
        result = response.json()                              # http text to python dict
        print("result :",result)

        if result.get("status") ==  "COMPLETE":
            order = Order.objects.get(user = request.user , is_ordered = False,order_number=order_number)
            payment = Payment(
               user = request.user,
               payment_id = result.get("ref_id"),
               transaction_uuid = result.get("transaction_uuid"),
               payment_method = order.payment_option,
               amount_paid = result.get("total_amount"),
               status = result.get("status")
            )
            payment.save()
            if order:
                order.payment = payment
                order.is_ordered = True
                order.save()
            return True
        else:
            return False
    except Exception as e:
        return False
    
def Khalti_payment(request,order_number):
    return HttpResponse("Coming Soon !")

def Payment_Success(request):

    if not request.session.get('allow_payment'):
        return redirect('cart')
    
    data_encoded = request.GET.get('data')
    order_number = request.session.get("pending_order_number") 
    success= verify_esewa_payment(request,data_encoded,order_number)     # Verification

    print("success:",success)
    request.session.pop("pending_order_number", None)
    request.session.pop('allow_payment', None)
    
    if success:
        return render(request,'orders/payment_success.html')
    else:
        return render(request,'orders/payment_failure.html')

def Payment_Failure(request):
    if not request.session.get('allow_payment'):
        return redirect('cart')

    request.session.pop('allow_payment', None)
    return render(request,'orders/payment_failure.html')

# COD Logic starts from here
def generate_payment_id():
    number_part = str(random.randint(1, 9999)).zfill(4)
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    return f"{number_part}{random_part}"

def COD_payment(request,order_number,total = 0,tax = 0,grand_total = 0):

    current_user = request.user
    cart_items = CartItem.objects.filter(user = current_user)
   
    for item in cart_items:
        total += (item.product.price * item.quantity)   
    tax = (2 * total)/100
    grand_total = total + tax

    order = Order.objects.get(user = current_user , is_ordered = False , order_number=order_number)

    payment = Payment(
        user = current_user,
        payment_id = generate_payment_id(),
        payment_method = order.payment_option,
        amount_paid = grand_total,
        status = "COMPLETE"
    )
    payment.save()
    if order:
        order.payment = payment
        order.is_ordered = True
        order.save()
    

    context = {
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
        'cart_items': cart_items,
        'order' : order,
    }
    return render(request,'orders/payment.html',context)