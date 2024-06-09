from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager
import random

# Create your models here.

class UserManager(BaseUserManager):

    def create_user_otp(self, phonenumber, otp_code):
        """
        create user otp for verify user signup
        """
        if not phonenumber:
            raise ValueError("phone number is required!")
        rand_int = random.randrange(100000,999999)
        user = self.model(phonenumber=phonenumber, otp_code=rand_int)
        user.phoneverified = False
        user.save()
        return user

    def create_user(self, phonenumber, password=None, **extra_fields):
        """Create user after verify otp code"""
        if not phonenumber:
            raise ValueError("phone number is required!")
        user = self.model(phonenumber=phonenumber, **extra_fields)
        user.phoneverified = True
        user.set_password(password)
        user.save()
        return user
    

    def create_superuser(self, phonenumber, password=None, **extra_fields):
        """Create superuser with given phone number and password"""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(phonenumber, password, **extra_fields)
    



class User(AbstractUser):
    username = None
    phonenumber = models.CharField(max_length=11, unique=True,)
    otp_code = models.CharField(max_length=6,null=True, blank=True)
    storename = models.CharField(max_length=100)
    phoneverified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'phonenumber'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self) -> str:
        return self.first_name + " " + self.last_name 

