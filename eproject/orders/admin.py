from django.contrib import admin
from orders.models import Payment,Order,OrderProduct

# Register your models here.
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user','payment_id','transaction_uuid','payment_method','amount_paid','status','created_at']  
    list_display_links = ['payment_id']

class OrderProductInline(admin.TabularInline):
    model = OrderProduct 
    extra = 0
    readonly_fields = ['user','payment','order','product','variations','quantity','product_price','ordered']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user','payment','order_number','transaction_uuid','full_name','phone','email','full_address','payment_option','order_total','tax','status','is_ordered','created_at','updated_at']
    list_display_links = ['order_number']
    readonly_fields = ['created_at', 'updated_at']
    list_filter = ['status','is_ordered']
    search_fields = ['order_number','full_name']
    list_per_page = 20
    inlines = [OrderProductInline]

admin.site.register(OrderProduct)  