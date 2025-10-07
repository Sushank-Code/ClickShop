from django.shortcuts import render,redirect
from accounts.forms import RegistrationForm
from django.contrib import messages 
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required

# Create your views here.

def registration(request):
    if request.method == "POST":
        rform = RegistrationForm(request.POST)
        if rform.is_valid():
            messages.success(request,"Registration Successful")
            rform.save()
            return redirect('Registration')
    else:
        rform = RegistrationForm()
    context = {
        'rform' : rform
    }
    return render(request,'accounts/registration.html',context)

def signin(request):

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request,"Both fields are required")

        else:
            user = authenticate(request,email= email,password= password)
            
            if user is not None:
                login(request,user)
                messages.success(request,"Login Successful")
                return redirect('Signin')
            else:
                messages.error(request,"Invalid login credentials")

    return render(request,'accounts/signin.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged Out !")
    return redirect('Signin') 