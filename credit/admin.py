from django.contrib import admin
from .models import Customer, AccountsReceivable, Payment, Factor, Products
# Register your models here.


class CustomerAdmin(admin.ModelAdmin):
    model = Customer
    list_display = ['full_name', 'phone_number' ,'seller', 'joined', 'active_credit']
    list_display_links = ['full_name', 'phone_number','seller',  'joined', 'active_credit']
    list_filter = ['phone_number','seller', 'active_credit']

class AccountsReceivableAdmin(admin.ModelAdmin):
    model = AccountsReceivable
    list_display = ['id', 'type' ,'debit', 'created']
    list_display_links = ['id', 'type' ,'debit', 'created']

class FactorAdmin(admin.ModelAdmin):
    model = Factor
    list_display = ['code', 'seller' ,'customer', 'created', 'accountsReceivable',]
    list_display_links = ['code',]
    list_filter = ['seller', 'customer', 'accountsReceivable',]
    search_fields = ['code',]

admin.site.register(AccountsReceivable, AccountsReceivableAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Factor, FactorAdmin)

admin.site.register(Payment)
admin.site.register(Products)