from django import forms
from .models import User
import re

class SignupForm(forms.Form):
    store_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    seller_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'class': "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_phone_number(self):
        mobile_regex = "^09(1[0-9]|3[1-9])-?[0-9]{3}-?[0-9]{4}$"
        phone_number = self.cleaned_data.get('phone_number')
        if(re.search(mobile_regex, phone_number)):
            if User.objects.filter(phone_number=phone_number).exists():
                self.add_error('phone_number', "شماره همراه قبلا ثبت نام شده است")
            else:
                return phone_number
        self.add_error('phone_number', "شماره همراه نامعتبر است")
        
    def clean(self):
        cleaned_data = super().clean()
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if re.match("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])", password):
            if len(password) >= 8:
                if password == password_confirm:
                    return cleaned_data
                else:
                    self.add_error('password', "رمز عبور و تکرار آن ها یکسان نیستند")
            else:
                self.add_error('password', "رمز عبور باید ۸ کارکتر یا بیشتر باشد")
        else:
             self.add_error('password', "رمز عبور باید دارای حروف کوچک و بزرگ همراه با عدد و ... باشد")
             self.add_error('password_confirm', "رمز عبور باید دارای حروف کوچک و بزرگ همراه با عدد و ... باشد")


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        for field_name in self.errors:
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs.update({'class': 'form-control is-invalid'})
            
        