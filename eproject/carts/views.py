from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product
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

    # This Make sure user has a cart tied to their session
    cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))

    # adding product to cart item 
    try:
        cart_item = CartItem.objects.get(product = product ,cart = cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:        # If cart not exist , place the product in cart
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
        )
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

def cart(request,total = 0,quantity = 0,cart_items = None):
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