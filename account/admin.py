from django.contrib import admin
from .models import User
# Register your models here.


class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ['first_name','last_name','phonenumber', 'storename', 'phoneverified']
    list_filter =  ['phoneverified']
    list_display_links = ['phonenumber', 'first_name']


admin.site.register(User, UserAdmin)