from django.contrib import admin
from orders.models import Payment,Order,OrderProduct

# Register your models here.
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user','payment_id','transaction_uuid','payment_method','amount_paid','status'] 
    list_display_links = ['payment_id']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user','payment','full_name','phone','email','full_address','payment_option','order_total','tax','status','is_ordered']
    list_display_links = ['full_name']
    list_filter = ['status','is_ordered']
    search_fields = ['order_number','full_name']
    list_per_page = 20

admin.site.register(OrderProduct)