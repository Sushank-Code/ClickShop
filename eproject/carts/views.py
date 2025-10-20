from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from store.models import Product,Variation
from carts.models import CartItem
# from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.decorators import login_required
from django.contrib import messages 

# Create your views here.

def add_cart(request,product_id):

    product = Product.objects.get(id = product_id)
    current_user = request.user

    # For authenticated user
    if current_user.is_authenticated:
        
        product_variation = []
        if request.method == "POST":
            for key, value in request.POST.items():
                if key != "csrfmiddlewaretoken":
                  
                    try:
                        variation = Variation.objects.get(product=product, variation_category__iexact = key ,variation_value__iexact = value) 
                        product_variation.append(variation)
                    except Exception as e:
                        raise e

        is_cart_item_exists = CartItem.objects.filter(user = current_user, product = product).exists() 

        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(user = current_user,product = product )

            ex_var_list = []
            cart_item_id = []
            for item in cart_item:
                existing_variations = item.variations.all()
                ex_var_list.append(list(existing_variations))
                cart_item_id.append(item.id)

            if product_variation in ex_var_list:

                cart_item_index = ex_var_list.index(product_variation)     
                item_id = cart_item_id[cart_item_index]                                
                item = CartItem.objects.get(product=product,id=item_id)
                item.quantity += 1
                item.save()

            else:                                                     

                item = CartItem.objects.create(product=product,user = current_user,quantity = 1)
                if len(product_variation) > 0 :
                    item.variations.clear()
                    for variation in product_variation :   
                        item.variations.add(variation)

                item.save()

        else :                                         
        
            cart_item = CartItem.objects.create(product=product,user=current_user,quantity = 1)
            if len(product_variation) > 0 :
                cart_item.variations.clear()
                for variation in product_variation :    
                    cart_item.variations.add(variation)
        return redirect('cart')
    
    
    # for non authenticated user
    else:        
        messages.info(request,"Please Sign in before adding to cart")
        return redirect('Signin')

@login_required(login_url='Signin')
def remove_cart(request,product_id,cart_item_id):
    
    product = get_object_or_404(Product,id = product_id)

    if request.user.is_authenticated:
        item = CartItem.objects.get(user = request.user, product = product,id = cart_item_id)
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
 
    return redirect('cart')

@login_required(login_url='Signin')
def remove_all(request,product_id,cart_item_id):
    
    product = get_object_or_404(Product,id = product_id)

    if request.user.is_authenticated:
        item = CartItem.objects.get(user = request.user, product = product,id = cart_item_id)
        item.delete()
    return redirect('cart')

def cart(request,total = 0,quantity = 0,tax = 0,grand_total = 0,cart_items = None):

 
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user = request.user, is_active = True)
    
        for item in cart_items:    
            total += (item.product.price * item.quantity)   # every product in cart's = total
            quantity += item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
 

        context = {
            'total':total,
            'quantity':quantity, 
            'cart_items':cart_items,
            'tax' : tax,
            'grand_total' : grand_total
        }
        return render (request,'carts/cart.html',context)
    
    else:
        messages.info(request,"Please Sign in before adding to cart")
        return redirect('Signin')

@login_required(login_url='Signin')
def checkout(request,total = 0,quantity = 0,tax = 0,grand_total = 0,cart_items = None):

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user = request.user, is_active = True)
            
        if cart_items:
            for item in cart_items:    
                total += (item.product.price * item.quantity)   
                quantity += item.quantity
            tax = (2 * total)/100
            grand_total = total + tax

            context = {
                'total':total,
                'quantity':quantity,
                'cart_items':cart_items,
                'tax' : tax,
                'grand_total' : grand_total
            }
            return render(request,'carts/checkout.html',context)
        else:
            return redirect('cart')
