from django.shortcuts import render
from store.models import Product,ReviewRating

# Create your views here.

def HomeView(request):
    products = Product.objects.filter(is_available = True)
    
    context = {
        'products' : products ,
    }
    return render(request,'kartapp/home.html',context)