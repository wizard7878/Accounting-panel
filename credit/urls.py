from django.urls import path, include
from .views import index, CustomerCredit

urlpatterns = [
    path('', index),
    path('<int:id>/customer/', CustomerCredit.as_view(), name='customer')

]