from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from accounts.models import Account,UserProfile
from django.utils.html import format_html

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

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(object.profile_picture.url))
    thumbnail.short_description = 'Profile Picture'
    list_display = [ 'user', 'full_address','city', 'state', 'country']