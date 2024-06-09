from django.shortcuts import render , redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.views import View
from .form import SignupForm
from .models import User
# Create your views here.

def signupOtp(request):
    if request.method == "POST":
        signupForm = SignupForm(request.POST)
        if signupForm.is_valid():
            form_data = signupForm.cleaned_data
            data = {
                'phonenumber':form_data['phone_number'],
                'password':form_data['password'],
            }
            user = User.objects.create_user(**data)
            user.full_name = form_data['seller_name']
            user.storename = form_data['store_name']
            user.save()
            return redirect("verify_otp", id=user.id)
        else:
            return render(request, "auth/sign-up.html", context={'signupform': signupForm})
    else:
        signupForm = SignupForm()
        return render(request, "auth/sign-up.html", context={'signupform': signupForm})
    

def verify_otp(request, id):
    user = User.objects.get(id=id)
    user.otp_code = '123456'
    user.save()
    if request.method == "POST":
        otp_number = ''
        for number in range(1,7):
            otp_number += request.POST[f'num{number}']
        if user.otp_code == otp_number:
            user.otp_code = None
            user.phoneverified = True
            user.save()
            return HttpResponse("OK")
    return render(request, "auth/2fa.html", {'phonenumber': user.phonenumber})