from django.contrib import admin
from .models import Customer, AccountsReceivable, Payment, Factor, Products, TextMessage
# Register your models here.

class CustomerInline(admin.TabularInline):
    model = Customer.AccountsReceivable.through
    extra = 1
    verbose_name = "حساب مشتری"

class AccountsReceivableInline(admin.TabularInline):
    model = AccountsReceivable.payment.through
    extra = 1
    verbose_name = "پرداختی مربوط به این حساب"

class CustomerAdmin(admin.ModelAdmin):
    model = Customer
    list_display = ['full_name', 'phone_number' ,'seller', 'joined', 'active_credit']
    list_display_links = ['full_name', 'phone_number','seller',  'joined', 'active_credit']
    list_filter = ['phone_number','seller', 'active_credit']
    inlines = [CustomerInline]

class AccountsReceivableAdmin(admin.ModelAdmin):
    model = AccountsReceivable
    list_display = ['id', 'type' ,'debit', 'created']
    list_display_links = ['id', 'type' ,'debit', 'created']
    inlines = [AccountsReceivableInline]
    

class FactorAdmin(admin.ModelAdmin):
    model = Factor
    list_display = ['code', 'seller' ,'customer', 'created', 'accountsReceivable',]
    list_display_links = ['code',]
    list_filter = ['seller', 'customer', 'accountsReceivable',]
    search_fields = ['code',]

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_date','installment',]

admin.site.register(AccountsReceivable, AccountsReceivableAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Factor, FactorAdmin)

admin.site.register(Payment, PaymentAdmin)
admin.site.register(Products)
admin.site.register(TextMessage)



