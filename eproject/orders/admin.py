from django.contrib import admin
from orders.models import Payment,Order,OrderProduct

# Register your models here.
admin.site.register(Payment)
admin.site.register(Order)
admin.site.register(OrderProduct)