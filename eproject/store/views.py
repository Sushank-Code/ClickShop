from django.shortcuts import render,get_object_or_404,redirect
from kartapp.models import Category
from store.models import Product,ReviewRating,ProductGallery
from orders.models import OrderProduct
from store.forms import ReviewForm

from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages 

# Create your views here.
 
def StoreView(request,category_slug=None):

    if category_slug :
        categories = get_object_or_404(Category, slug = category_slug) # single obj
        # print(categories)
        products = Product.objects.filter(category = categories,is_available = True) 

        paginator = Paginator(products,2)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)  
        product_count = products.count()
    else :
        products = Product.objects.filter(is_available = True).order_by('id')
        paginator = Paginator(products,3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)    # return the page objects
        product_count = products.count()
    context = {
        'products' : paged_products ,
        'product_count' : product_count
    }
    return render(request,'store/store.html',context)

def product_detail(request,category_slug=None,product_slug=None):

    try:
        if category_slug and product_slug:
            
            categories = get_object_or_404(Category, slug=category_slug)
            single_product = get_object_or_404(Product, slug=product_slug, category=categories,is_available=True)       
            reviewform = ReviewForm()
        else:
            single_product = None
    except Exception as e:
        raise e
    
    if request.user.is_authenticated:
            orderproduct = OrderProduct.objects.filter(
                user=request.user,
                product_id=single_product.id,
                ordered=True,
            ).exists()
    else:
        orderproduct = None

    # Get the review for specific product
    reviews = ReviewRating.objects.filter(
        product_id=single_product.id,
        status=True,
    ).select_related('user', 'user__userprofile')

    # product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    
    context = { 
        'single_product' : single_product,
        'reviewform':reviewform,
        'orderproduct': orderproduct,
        'reviews':reviews,
        'product_gallery' : product_gallery
    }
    return render(request,'store/product_detail.html',context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
        if keyword:
            searched_products = Product.objects.filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
            ).order_by('created_date')
            product_count = searched_products.count()
        else:
            return redirect('store')
    context = {
        'products' : searched_products,
        'product_count' : product_count
    }
    
    return render(request,'store/store.html',context)   

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    product = get_object_or_404(Product, id=product_id)
    redirect_url = url or product.get_url()

    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to post a review.')
        return redirect('Signin')

    has_purchased = OrderProduct.objects.filter(
        user=request.user,
        product_id=product_id,
        ordered=True,
    ).exists()
    if not has_purchased:
        messages.error(request, 'You must purchase this product to post a review.')
        return redirect(redirect_url)

    if request.method == 'POST':

        try:
            review = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=review)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(redirect_url)
        
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.rating = form.cleaned_data['rating']
                
                data.product = product
                data.user = request.user
                data.ip = request.META.get('REMOTE_ADDR')
                data.save()

                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(redirect_url)
