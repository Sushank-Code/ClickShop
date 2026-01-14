from django.shortcuts import render,redirect,get_object_or_404
from accounts.forms import RegistrationForm,CustomPasswordResetForm,CustomSetPasswordForm,UserProfileForm,UserForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages 
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from accounts.models import Account,UserProfile
from orders.models import Order

# user activation
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode ,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# password reset
from django.contrib.auth.views import PasswordResetView,PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

# Create your views here.

def registration(request):

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        rform = RegistrationForm(request.POST)
        if rform.is_valid():
            user = rform.save(commit=False)
            user.is_active = False                              # user will be inactive until email is verified
            user.save()
            UserProfile.objects.create(user=user)
            # user activation

            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = rform.cleaned_data.get('email')
            email = EmailMessage(mail_subject,message,to=[to_email])
            email.content_subtype = 'html'
            email.send()

            return redirect('/accounts/signin/?command=verification&email='+ to_email)
    else:
        rform = RegistrationForm()
    context = {
        'rform' : rform
    }
    return render(request,'accounts/registration.html',context) 

def activate(request,uidb64,token):
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,"Your account has been successfully verified. Please log in to continue.")
        return redirect('Signin')
    
    else:
        messages.error(request,"Activation link is invalid or has expired. Please register again or request a new activation email.")
        return redirect('Registration')

def signin(request):

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request,"Both fields are required")

        else:
            user = authenticate(request,email= email,password= password)
            
            if user is not None: 
              
                login(request,user)
                # messages.success(request, "You are now logged in.")
                return redirect('home')
            else:
                messages.error(request,"Invalid login credentials")

    return render(request,'accounts/signin.html')

@login_required(login_url='Signin')
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('Signin') 

@login_required(login_url='Signin')
def dashboard(request):
    order_count = Order.objects.filter(user = request.user,is_ordered = True ).order_by('created_at').count()
    userprofile = UserProfile.objects.get(user = request.user)
    context = {
        'order_count' : order_count ,
        'userprofile' : userprofile
    }
    return render(request,'accounts/dashboard.html',context)

@login_required(login_url='Signin')
def My_Orders(request):
    orders = Order.objects.filter(user = request.user,is_ordered = True ).order_by('-created_at')
    context = {
        'orders' : orders,
    }
    return render(request,'accounts/my_orders.html',context)

@login_required(login_url='Signin')
def Edit_Profile(request):

    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('Edit_Profile') 
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form, 
        'userprofile': userprofile,
    }

    return render(request, 'accounts/edit_profile.html', context)

# Change Password after Logging
@login_required
def password_change_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            logout(request)
            messages.success(request,"Password change sucessfully! Login again with new password")
            return redirect("Signin")
    else:
        form = PasswordChangeForm(user = request.user)
    return render(request,'accounts/password_change.html',{'form':form})

# forgot password

class CustomPasswordResetView(SuccessMessageMixin,PasswordResetView): 
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset_form.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    html_email_template_name = 'accounts/password_reset_email.html'
    success_message = "Reset link sent to your email."
    success_url = reverse_lazy('Signin')

    def send_mail(self, context, from_email, to_email,html_email_template_name):
        
        body = render_to_string(html_email_template_name, context)
        email = EmailMessage(
            body=body,
            from_email=from_email,
            to=[to_email]  
        )
        email.content_subtype = 'html'
        email.send()

class CustomPasswordResetConfirmView(SuccessMessageMixin,PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'accounts/password_reset_confirm.html'
    success_message = "Password reset successful. Please login."
    success_url = reverse_lazy('Signin')