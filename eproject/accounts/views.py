from django.shortcuts import render,redirect
from accounts.forms import RegistrationForm

# Create your views here.
def registration(request):
    if request.method == "POST":
        rform = RegistrationForm(request.POST)
        if rform.is_valid():
            username = rform.cleaned_data['email'].split("@")[0]
            rform.save()
            return redirect('Login')
    else:
        rform = RegistrationForm()
    context = {
        'rform' : rform
    }
    return render(request,'accounts/registration.html',context)


def login(request):
    return render(request,'accounts/login.html')

def logout_view(request):
    pass