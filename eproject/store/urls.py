from django.urls import path
from store import views

urlpatterns = [
    path('',views.StoreView,name='store'),
    path('category/<slug:category_slug>/',views.StoreView,name='product_by_category'),#dynamic_Url 
    path('category/<slug:category_slug>/<slug:product_slug>/',views.product_detail,name='product_detail'), 
    path('search/',views.search,name='search'),
]

