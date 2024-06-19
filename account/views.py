from django.shortcuts import render , redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from .form import SignupForm, SigninForm
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
            send_otp_code(user)
            return redirect("verify_otp", id=user.id)
        else:
            return render(request, "auth/sign-up.html", context={'signupform': signupForm})
    else:
        signupForm = SignupForm()
        return render(request, "auth/sign-up.html", context={'signupform': signupForm})
    

def verify_otp(request, id):
    user = User.objects.get(id=id)
    if request.method == "POST":
        if request.POST.get('send-sms-again') == '':
            code = send_otp_code(user)
            return redirect("verify_otp", id=user.id)
        otp_number = ''
        for number in range(1,7):
            otp_number += request.POST[f'num{number}']
        if user.otp_code == int(otp_number):
            user.otp_code = None
            user.phoneverified = True
            user.save()
            login(request, user)
            return HttpResponse("OK")  ####### Home Page
    return render(request, "auth/2fa.html", {'user': user})


def loginOtp(request):
    if request.method == 'POST':
        signinform = SigninForm(request.POST)
        if signinform.is_valid():
            phone_number = signinform.cleaned_data['phone_number']
            password = signinform.cleaned_data['password']
            user = authenticate(request, phonenumber=phone_number, password=password)
            if user is not None:
                send_otp_code(user)
                return redirect("verify_otp", id=user.id)
            else:

                signinform.add_error("password", "شماره همراه یا رمز عبور اشتباه است")
                return render(request, "auth/sign-in.html", {'signinform': signinform})
        else:
            return render(request, "auth/sign-in.html", {'signinform': signinform})

    signinform = SigninForm()
    return render(request, "auth/sign-in.html", {'signinform': signinform})

def logoutView(request):
    logout(request)
    return redirect('loginOtp')



# Tools
import random
def send_otp_code(user):
    code = random.randint(100000, 999999)
    user.otp_code = code
    user.save()
    
    # send sms

    return code