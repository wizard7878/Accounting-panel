from django.urls import path, include
from .views import (
    index, 
    CustomerCredit,
    CustomerRialiCreditView, 
    CustomerLongCreditView, 
    CustomerGramiCreditView
    )

urlpatterns = [
    path('', index, name= 'credit'),
    path('<int:id>/customer/', CustomerCredit.as_view(), name='customer'),
    path('<int:customerId>/customer/<int:creditId>/Long-term-customer-account', CustomerLongCreditView.as_view(), name='long-customer-account'),
    path('<int:customerId>/customer/<int:creditId>/grami-customer-account', CustomerGramiCreditView.as_view(), name='grami-customer-account'),
    path('<int:customerId>/customer/<int:creditId>/riali-customer-account', CustomerRialiCreditView.as_view(), name='riali-customer-account'),

]