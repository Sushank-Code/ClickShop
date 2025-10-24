from django.urls import path
from orders import views

urlpatterns = [

    path('place_order/',views.Place_Order,name='place_order'),
    path('payment/',views.Payment,name='payment'),
    path('payment_success/',views.Payment_Success,name='payment_success'),
    path('payment_failure/',views.Payment_Failure,name='payment_failure'),

]