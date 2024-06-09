from django.urls import path, include
from .views import signupOtp, verify_otp

urlpatterns = [
    path('signup/', signupOtp, name='signup'),
    path('<uuid:id>/verify-otp/', verify_otp, name='verify_otp')

]