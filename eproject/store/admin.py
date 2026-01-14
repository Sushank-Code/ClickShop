from django.contrib import admin
from store.models import Product,Variation,ReviewRating

# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name','price','stock','category','is_available','created_date','modified_date']
    list_display_links = ['product_name']
    prepopulated_fields = {'slug':('product_name',)}

@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ['product','variation_category','variation_value','is_active']
    list_display_links = ['product']
    list_editable = ['is_active']
    list_filter = ['product','variation_category','variation_value','is_active']

@admin.register(ReviewRating)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user','product','rating','subject','review','status','created_at']
    list_display_links = ['product']
    list_editable = ['status']
      