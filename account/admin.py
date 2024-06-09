from django.contrib import admin
from .models import User
# Register your models here.


class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ['id', 'full_name','phonenumber', 'storename', 'phoneverified']
    list_filter =  ['id', 'phoneverified']
    list_display_links = ['id','phonenumber', 'full_name']


admin.site.register(User, UserAdmin)