from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from accounts.models import Account,UserProfile
from django.utils.html import format_html
import admin_thumbnails

# Register your models here.
@admin.register(Account)
class AccountAdmin(UserAdmin):
    model = Account
    list_display = ['id','email','username','is_active','is_staff','is_superuser','date_joined','last_login']
    list_display_links = ['email']

    readonly_fields = ['password','date_joined','last_login']
    ordering = ['email','id']
    list_filter = []
    fieldsets = ()
    filter_horizontal = []

@admin_thumbnails.thumbnail('profile_picture')
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [ 'user','full_address','city', 'state', 'country'] 