from django.shortcuts import render,get_object_or_404,HttpResponse,redirect
from kartapp.models import Category
from store.models import Product
from django.core.paginator import Paginator
from django.db.models import Q

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
        else:
            single_product = None
    
    except Exception as e:
        raise e
    
    context = {
        'single_product' : single_product,
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