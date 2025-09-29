from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from store.models import Product,Variation
from carts.models import Cart
from carts.models import CartItem
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

def _cart_id (request):                      # helper function = private & internal use 
    cart = request.session.session_key       # get the session Id  
    if not cart:
        cart = request.session.create()      # if none, creates the session Id
    return cart

def add_cart(request,product_id):
    product = Product.objects.get(id = product_id)

    # variation starts
    product_variation = []

    if request.method == "POST":
        for key, value in request.POST.items():
            if key != "csrfmiddlewaretoken":
                # print(key, value)

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact = key ,variation_value__iexact = value) 
                    product_variation.append(variation)
                except Exception as e:
                    print("Error : ", e)



    # This Make sure user has a cart tied to their session
    cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))

    # adding product to cart item 
    try:
        cart_item = CartItem.objects.get(product = product ,cart = cart)
        if len(product_variation) > 0 :
            cart_item.variations.clear()
            for variation in product_variation :  # multiple varation here
                cart_item.variations.add(variation)

        cart_item.quantity += 1
        cart_item.save()

    except CartItem.DoesNotExist:        # If cart not exist , place the product in cart
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
        )
        if len(product_variation) > 0 :
            cart_item.variations.clear()
            for variation in product_variation :  # multiple varation here
                cart_item.variations.add(variation)
    return redirect('cart')

def remove_cart(request,product_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product,id = product_id)
    item = CartItem.objects.get(cart = cart, product = product)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('cart')

def remove_all(request,product_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product,id = product_id)
    item = CartItem.objects.get(cart = cart, product = product)
    item.delete()
    return redirect('cart')

def cart(request,total = 0,quantity = 0,tax=0,grand_total = 0 ,cart_items = None):
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.filter(cart = cart, is_active = True)
        for item in cart_items:    
            total += (item.product.price * item.quantity)   # every product in cart's = total
            quantity += item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax' : tax,
        'grand_total' : grand_total
    }
    return render (request,'carts/cart.html',context)