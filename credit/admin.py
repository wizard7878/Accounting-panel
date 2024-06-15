from django.contrib import admin
from .models import Customer, AccountsReceivable, Payment, Factor, Products
# Register your models here.


class CustomerAdmin(admin.ModelAdmin):
    model = Customer
    list_display = ['full_name', 'phone_number' ,'seller', 'joined', 'active_credit']
    list_display_links = ['full_name', 'phone_number','seller',  'joined', 'active_credit']
    list_filter = ['phone_number','seller', 'active_credit']

admin.site.register(Customer, CustomerAdmin)
admin.site.register(AccountsReceivable)
admin.site.register(Payment)
admin.site.register(Factor)
admin.site.register(Products)