from django.urls import path
from accounts import views

urlpatterns = [
    path('registration/',views.registration,name='Registration'),
    path('login/',views.login,name='Login'),
    path('logout/',views.logout_view,name='Logout'),
] 