from django.db import models
from django_jalali.db import models as jmodels
from account.models import User
# Create your models here.

class Customer(models.Model):
    phone_number = models.CharField(max_length=11)
    full_name = models.CharField(max_length=80)
    address = models.TextField()
    avatar = models.ImageField(null=True, blank=True)
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    referal = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
    joined = jmodels.jDateField(auto_now_add=True)
    active_credit = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.full_name