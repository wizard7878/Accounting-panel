from django.urls import path, include
from .views import signupOtp, verify_otp, loginOtp

urlpatterns = [
    path('signup/', signupOtp, name='signup'),
    path('<uuid:id>/verify-otp/', verify_otp, name='verify_otp'),
    path('login/', loginOtp, name='loginOtp')

]