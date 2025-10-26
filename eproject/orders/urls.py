from django.urls import path
from orders import views

urlpatterns = [

    path('place_order/',views.Place_Order,name='place_order'),
    path('payment/esewa/<str:order_number>/', views.eSewa_payment, name='esewa_payment'),
    path('payment/khalti/<str:order_number>/', views.Khalti_payment, name='khalti_payment'),
    path('payment/cod/<str:order_number>/', views.COD_payment, name='cod_payment'),
    path('payment_success/',views.Payment_Success,name='payment_success'),
    path('payment_failure/',views.Payment_Failure,name='payment_failure'),

]