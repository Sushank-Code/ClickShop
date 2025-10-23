from django.urls import path
from orders import views

urlpatterns = [
    path('place_order/',views.Place_Order,name='place_order'),
    path('payments/',views.Payments,name='payments'),
]