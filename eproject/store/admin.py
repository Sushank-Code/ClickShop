from django.contrib import admin
from store.models import Product,Variation,ReviewRating,ProductGallery
import admin_thumbnails
# Register your models here.

@admin_thumbnails.thumbnail('image')
class productgalleryinline(admin.TabularInline):
    model = ProductGallery
    extra = 1
    # can_delete = True
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name','price','stock','category','is_available','created_date','modified_date']
    list_display_links = ['product_name']
    prepopulated_fields = {'slug':('product_name',)}
    inlines = [productgalleryinline]

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
      
admin.site.register(ProductGallery)