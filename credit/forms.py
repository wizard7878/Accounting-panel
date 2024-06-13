from django import forms
import re

from .models import Customer

class CreateCustomerForm (forms.Form):
    phone_number = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'class': "form-control"}))

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('user', None)
        super(CreateCustomerForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        for field_name in self.errors:
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs.update({'class': 'form-control is-invalid'})

    def clean_phone_number(self):
        mobile_regex = "^09(1[0-9]|3[1-9])-?[0-9]{3}-?[0-9]{4}$"
        phone_number = self.cleaned_data.get('phone_number')
        if(re.search(mobile_regex, phone_number)):
            if Customer.objects.filter(seller=self.current_user, phone_number=phone_number).exists():
                self.add_error('phone_number', "شماره همراه قبلا ثبت نام شده است")
            else:
                return phone_number
        else:
            self.add_error('phone_number', "شماره همراه نامعتبر است")


class CustomerChangeInfoForm(forms.Form):
    full_name = forms.CharField(max_length=80, widget=forms.TextInput(attrs={'class': "form-control"}))
    phone_number = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'class': "form-control"}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': "form-control"}))

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('user', None)
        self.current_customer = kwargs.pop('current_customer', None)
        super(CustomerChangeInfoForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        for field_name in self.errors:
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs.update({'class': 'form-control is-invalid'})


    def clean_phone_number(self):
        mobile_regex = "^09(1[0-9]|3[1-9])-?[0-9]{3}-?[0-9]{4}$"
        phone_number = self.cleaned_data.get('phone_number')
        if(re.search(mobile_regex, phone_number)):
            if Customer.objects.filter(seller=self.current_user, phone_number=phone_number).exists():
                if phone_number != self.current_customer.phone_number:
                    self.add_error('phone_number', "شماره همراه قبلا ثبت نام شده است")
                else:
                    return phone_number
            else:
                return phone_number
        else:
            self.add_error('phone_number', "شماره همراه نامعتبر است")

        
        