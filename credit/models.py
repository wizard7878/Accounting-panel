from django.db import models
from django_jalali.db import models as jmodels
from django.utils.text import slugify
from account.models import User
import datetime
import itertools
import random
# Create your models here.




class Payment(models.Model):
    payment_date = jmodels.jDateField(default=datetime.datetime.now())
    liquidated_price = models.IntegerField(verbose_name="فی آبشده")
    payment_received = models.IntegerField(verbose_name="رسیده")
    installment = models.IntegerField(verbose_name="قسط")
    Account_balance_in_gram = models.FloatField(verbose_name="مانده به گِرم")
    Account_balance_in_rial = models.IntegerField(verbose_name="مانده به ریال", null=True, blank=True)

    def __str__(self) -> str:
        return str(self.payment_date)

class AccountsReceivable(models.Model):
    AccountsReceivable_CHOICES = (
        ('G', 'grami'),
        ('R', 'riali'),
        ('L', 'long-term'),
    )
    type = models.CharField(max_length=1, choices=AccountsReceivable_CHOICES, verbose_name="نوع حساب")
    created = jmodels.jDateField(auto_now_add=True)
    borrow = models.FloatField(null=True, blank=True,verbose_name="امانت")
    installments = models.IntegerField(null=True, blank=True, verbose_name="تعداد اقساط")
    interest_rates = models.FloatField(verbose_name="درصد سود", blank=True, null=True)
    debit = models.BooleanField(default=True,verbose_name="بدهی")
    payment = models.ManyToManyField(Payment, null=True, verbose_name="پرداختی ها")

    def __str__(self) -> str:
        return self.type + " " + str(self.created)


class Customer(models.Model):
    phone_number = models.CharField(max_length=11)
    full_name = models.CharField(max_length=80)
    address = models.TextField()
    avatar = models.ImageField(null=True, blank=True)
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    referal = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
    joined = jmodels.jDateField(auto_now_add=True)
    active_credit = models.BooleanField(default=False)
    AccountsReceivable = models.ManyToManyField(AccountsReceivable, null=True)

    def __str__(self) -> str:
        return self.full_name
    

class Factor(models.Model):
    created = jmodels.jDateField(auto_now_add=True)
    total_weight = models.FloatField(verbose_name="مجموع وزن به گرم")
    total_price = models.IntegerField(verbose_name="مجموع قیمت به ریال", null=True, blank=True)
    code = models.SlugField()
