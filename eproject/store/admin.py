from django.contrib import admin
from store.models import Product

# Register your models here.

@admin.register(Product)
class studentAdmin(admin.ModelAdmin):
    list_display = ['product_name','price','stock','category','is_available','created_date','modified_date']
    list_display_links = ['product_name']
    prepopulated_fields = {'slug':('product_name',)}