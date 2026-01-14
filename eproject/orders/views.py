from django.shortcuts import render,redirect,HttpResponse
from carts.models import CartItem
from orders.models import Order,Payment,OrderProduct
from orders.forms import OrderForm

# Order_number
import datetime,random,string

# payment gateway(Esewa)
import uuid,hmac,hashlib,base64,json,requests
from django.conf import settings

from django.db import transaction
from django.db.models import F
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

# Order_email
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Create your views here.

@require_POST
@login_required(login_url='Signin')
def Place_Order(request,total = 0,tax = 0,grand_total = 0):

    current_user = request.user
    cart_items = CartItem.objects.filter(user = current_user,is_active = True)
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
            order.transaction_uuid = str(uuid.uuid4())
            order.order_total = grand_total
            order.tax = tax
            order.ip = request.META.get('REMOTE_ADDR')

            order.save()                             # Must save before getting order id ( beacuse id only appear after saving)

            yr = int(datetime.date.today().strftime('%Y'))
            mt = int(datetime.date.today().strftime('%m'))
            dt = int(datetime.date.today().strftime('%d'))

            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")              # coverted to string                                        
            order_number = current_date + str(order.id)
            order.order_number = order_number
            order.save()                                    # Now , order_number is saved

            if order.payment_option == 'esewa':
                return redirect('esewa_payment',order_number=order.order_number)
            
            elif order.payment_option == 'khalti':
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

@login_required(login_url='Signin')
def eSewa_payment(request,order_number,total = 0,tax = 0,grand_total = 0):

    try:
        cart_items = CartItem.objects.filter(user = request.user,is_active=True)

        order = Order.objects.get(order_number=order_number,is_ordered = False)

        total = order.order_total - order.tax
        tax = order.tax 
        grand_total = order.order_total

        transaction_uuid = order.transaction_uuid
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
            'product_code' : product_code,                                     # test product_code
            'signed_field_name': "total_amount,transaction_uuid,product_code",
            'signature': signature,
            'esewa_url':settings.ESEWA_PAYMENT_URL ,                         # test url
            'success_url': "http://127.0.0.1:8000/orders/payment_success/",  # goes to suc View | Live ,use domain                      
            'failure_url': "http://127.0.0.1:8000/orders/payment_failure/",                        
        }
        return render(request, 'orders/payment.html',context) 
    
    except(Order.DoesNotExist):
        return redirect('home')

def verify_esewa_payment(request,payment_info,order):

    try:
        transaction_uuid = payment_info.get("transaction_uuid")  # accessing dictionary
        product_code = payment_info.get("product_code")
        total_amount = payment_info.get("total_amount")

        verify_url = settings.ESEWA_VERIFY_URL
        payload = {
            "product_code": product_code,
            "total_amount": total_amount,
            "transaction_uuid": transaction_uuid,
        }

        response = requests.get(verify_url, params=payload)    # Esewa does get (not post)
        result = response.json()                               # http text to python dict
        # print("result :",result)

        if result.get("status") ==  "COMPLETE":
            payment = Payment(
               user = order.user,
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

                # After payment logic
                Order_Product(request,order,payment)

    except Exception as e:
        # print(e)
        None
    
def Payment_Success(request):
    data_encoded = request.GET.get("data")          # esewa 
    order_number = request.GET.get("order_number")  # Cod

    try:
        # Gateway payment (eSewa)
        if data_encoded:  
            decoded_bytes = base64.b64decode(data_encoded)          # base64 text to raw bytes
            decoded_str = decoded_bytes.decode('utf-8')             # bytes to string
            payment_info = json.loads(decoded_str)                  # string with json text to python dictionary

            transaction_uuid = payment_info.get("transaction_uuid")

            order = Order.objects.get( transaction_uuid=transaction_uuid , is_ordered=False )

            if order.payment_option == 'esewa':
                verify_esewa_payment(request,payment_info,order)

        else:  
            # COD payment 
            if not order_number:
                return redirect('home')
            
            order = Order.objects.get(order_number=order_number, is_ordered=False)

            if order.payment_option == 'cod':
                verify_cod_payment(request,order)
        
        return redirect('order_invoice', order_number=order.order_number)

    except Order.DoesNotExist:
        return redirect('home')

def Payment_Failure(request):
    return render(request,'orders/payment_failure.html')

# COD Logic starts from here
def generate_payment_id():
    number_part = str(random.randint(1, 9999)).zfill(4)
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    return f"{number_part}{random_part}"

@login_required(login_url='Signin')
def COD_payment(request,order_number,total = 0,tax = 0,grand_total = 0):

    try:
        cart_items = CartItem.objects.filter(user = request.user,is_active=True)
        order = Order.objects.get(order_number=order_number,is_ordered = False)

        total = order.order_total - order.tax
        tax = order.tax
        grand_total = order.order_total


        context = {
            'total': total,
            'tax': tax,
            'grand_total': grand_total,
            'cart_items': cart_items,
            'order' : order,
        }
        return render(request,'orders/payment.html',context)
    
    except(Order.DoesNotExist):
        return redirect('home')

def verify_cod_payment(request,order):

    try:
        payment = Payment(
        user = order.user,
        payment_id = generate_payment_id(),
        payment_method = order.payment_option,
        amount_paid = order.order_total,
        status = "PENDING"
        )
        payment.save()
        if order:
            order.payment = payment
            order.is_ordered = True
            order.save()

            # After payment logic
            Order_Product(request,order,payment)

    except Exception as e:
        # print(e)
        None
    
# moving to order Product table 
def Order_Product(request,order,payment):
    cart_items = CartItem.objects.filter(user = request.user,is_active=True)

    with transaction.atomic():
        for item in cart_items:
            orderproduct = OrderProduct.objects.create(
                user = request.user,
                payment = payment,
                order = order,
                product = item.product,
                quantity = item.quantity,
                product_price = item.product.price,
                ordered = True,
            )
            orderproduct.variations.set(item.variations.all())
            orderproduct.save()

            # Reducing the stock of the product
            item.product.stock = F('stock') - item.quantity
            item.product.save()

        # Clearing Cart 
        cart_items.delete()
    
    # sending order received Email to User
    mail_subject = f"Order Confirmed - Order #{order.order_number}"
    message = render_to_string('orders/order_received_email.html',{
        'order': order,
    })
    to_email = request.user.email
    email = EmailMessage(mail_subject,message,to=[to_email])
    email.content_subtype = 'html'
    email.send()

@login_required(login_url='Signin')
def order_invoice(request, order_number):
    try:
        order = Order.objects.get(  
            order_number=order_number,
            user=request.user,
            is_ordered=True
        )

        order_products = OrderProduct.objects.filter(order=order)
        subtotal = 0 
        for i in order_products:
            subtotal += i.product.price * i.quantity

        context = {
            'order': order,
            'order_products': order_products,
            'subtotal' : subtotal
        }

        return render(request, 'orders/payment_success.html', context)

    except Order.DoesNotExist:
        return redirect('home')

def Khalti_payment(request,order_number):
    return HttpResponse("Coming Soon !")