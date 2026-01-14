from django import forms
from accounts.models import Account,UserProfile
from django.contrib.auth.forms import UserCreationForm,PasswordResetForm,SetPasswordForm
from django.core.validators import EmailValidator

class RegistrationForm(UserCreationForm):

    # override form fields to set widgets
    password1 = forms.CharField(
        label='Create Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter password',
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repeat password',
        })
    )
  
    class Meta:
        model = Account
        fields = ["username","phone","email","password1","password2"]

        labels = {
            'username' : 'UserName',
            'phone' : 'Phone Number',
            'email' : 'Email Address',
        } 

        widgets = {
            'username':forms.TextInput(attrs={
                'placeholder':'Enter your username',
                'autocomplete':'off',
            }),
            'phone':forms.TextInput(attrs={
                'placeholder':'Enter the phone number',
            }),
            'email':forms.EmailInput(attrs={
                'placeholder':'Valid Email Address',
                'autocomplete':'off',
            }),
        }

    # To apply widget for every field and single field (also hidden)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

        # Remove autofocus from all fields
        for field in self.fields.values():
            if 'autofocus' in field.widget.attrs:
                del field.widget.attrs['autofocus']

    # Validation
    
    def clean_username(self):   
        username = self.cleaned_data.get('username')

        if Account.objects.filter(username=username).exists():
            raise forms.ValidationError("UserName already taken")
    
        return username
    
    def clean_email(self):   
        email = self.cleaned_data.get('email')

        if Account.objects.filter(email = email).exists():
            raise forms.ValidationError("Email already exists")
    
        validator = EmailValidator(message="Enter a valid email address")
        try:
            validator(email)
        except forms.ValidationError as e:
            raise forms.ValidationError(e.message)
        
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if Account.objects.filter(phone = phone).exists():
            raise forms.ValidationError("Phone number already registered")
        
        if not phone.isdigit():
            raise forms.ValidationError("Phone must contain only numbers")

        if len(phone) != 10 :
            raise forms.ValidationError("Phone number must be 10 digits")
        
        return phone
    
# Password reset

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Valid Email Address",
        })
    )

    def clean_email(self):   
        email = self.cleaned_data.get("email")
        if not Account.objects.filter(email = email).exists():
            raise forms.ValidationError("Invalid Email Address")
        return email
    
class CustomSetPasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

        self.fields['new_password1'].widget.attrs['placeholder'] = 'Create new password'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm password'

class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['username', 'phone']

    def __init__(self, *args, **kwargs):    
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean_phone(self): 
        phone = self.cleaned_data.get('phone')

        if not phone.isdigit():
            raise forms.ValidationError("Phone must contain only numbers")

        if len(phone) != 10 :
            raise forms.ValidationError("Phone number must be 10 digits")
        
        return phone

class UserProfileForm(forms.ModelForm):
    
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    
    class Meta:
        model = UserProfile
        fields = ['address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
