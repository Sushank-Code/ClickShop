from django.contrib import admin
from carts.models import Cart,CartItem

# Register your models here.


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id','date_added']
    list_display_links = ['cart_id']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product','cart','quantity','is_active']
    list_display_links = ['product']