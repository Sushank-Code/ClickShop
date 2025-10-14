from django.urls import path
from accounts import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('registration/',views.registration,name='Registration'),
    path('signin/',views.signin,name='Signin'),
    path('logout/',views.logout_view,name='Logout'),
    path('activate/<uidb64>/<token>/',views.activate,name='Activate'),

    path('dashboard/',views.dashboard,name='Dashboard'),
    path('',views.dashboard,name='Dashboard'),

    path('forgotPassword/', views.CustomPasswordResetView.as_view(), name='forgotPassword'),
    path('reset/<uidb64>/<token>/',views.CustomPasswordResetConfirmView.as_view(),name='password_reset_confirm')
] 