from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin
 
# Create your models here.
  
class MyAccountManager(BaseUserManager):

    # Create a normal User 
    def create_user(self,first_name,last_name,username,email,password=None):

        if not email:
            raise ValueError("User must have an valid email address")
        if not username:
            raise ValueError("User must have an username")
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )
        user.set_password(password)
        user.save(using=self.db)
        return user
    
    # Create a super user
    def create_superuser(self,first_name,last_name,username,email,password):

        user = self.create_user(
            email=self.normalize_email(email),
            username = username,
            password= password,
            first_name = first_name,
            last_name = last_name,
        )
        user.is_active = True     
        user.is_staff = True
        user.is_superuser = True
      
        user.save(using=self.db)
        return user

class Account(AbstractBaseUser,PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50,unique=True)
    email = models.EmailField(max_length=254,unique=True)
    phone = models.CharField(max_length=50)

    # required
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username','first_name','last_name']
    
    objects = MyAccountManager()

    def __str__(self):
        return self.email
    
    # only super user can access anything ( not a nomal user)
    def has_perm(self, perm, obj = None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser
    