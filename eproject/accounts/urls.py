from django.urls import path
from accounts import views

urlpatterns = [
    path('registration/',views.registration,name='Registration'),
    path('signin/',views.signin,name='Signin'),
    path('logout/',views.logout_view,name='Logout'),
    path('activate/<uidb64>/<token>/',views.activate,name='Activate')
] 