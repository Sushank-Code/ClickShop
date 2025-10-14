from django.contrib import admin
from carts.models import CartItem
from django.utils.html import format_html

# Register your models here.

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product','get_variations','user','quantity','is_active'] 
    list_display_links = ['product']

    def get_variations(self, obj):
        variation_list = []
        for v in obj.variations.all():
            variation_list.append(f"{v.variation_category.capitalize()}: {v.variation_value.capitalize()}")
        return format_html("<br>".join(variation_list))
    get_variations.short_description = 'Variations'