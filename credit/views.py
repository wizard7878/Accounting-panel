from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import Customer
from .forms import CreateCustomerForm, CustomerChangeInfoForm
# Create your views here.

@login_required(login_url='/account/login/')
def index(request):
    customers = Customer.objects.filter(seller=request.user).order_by('-active_credit')
    paginator = Paginator(customers, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if request.GET.get('search_type'):
        if request.GET.get('search_type') == 'phone_number':
            if request.GET.get('name') == "":
                customers = Customer.objects.filter(seller=request.user)[:30]
            else:
                customers = Customer.objects.filter(seller=request.user, phone_number__startswith=request.GET.get('name'))
            
        elif request.GET.get('search_type') == 'full_name':
            if request.GET.get('name') == "":
                customers = Customer.objects.filter(seller=request.user)[:30]
            else:
                customers = Customer.objects.filter(seller=request.user, full_name__startswith=request.GET.get('name'))
        data = []
        for customer in customers:
            data.append(
                {
                    'phone_number': customer.phone_number,
                    'full_name': customer.full_name,
                    'joined': str(customer.joined),
                    'active_credit': customer.active_credit,
                    'address': customer.address,
                 }
                )
        
        return JsonResponse({'data': data})
    
    if request.method == 'POST':
        createCustomerForm = CreateCustomerForm(request.POST, user=request.user)
        if createCustomerForm.is_valid():
            new_customer = Customer.objects.create(seller= request.user ,phone_number=request.POST.get('phone_number'))
            return redirect('customer',new_customer.id)
        else:
            context = {
            'customers' : page_obj,
            'createCustomerForm': createCustomerForm
            }
            return render(request, "credit/index.html", context)
        

    createCustomerForm = CreateCustomerForm(user=request.user)    
    context = {
        'customers' : page_obj,
        'createCustomerForm': createCustomerForm
    }
    return render(request, "credit/index.html", context)


class CustomerCredit(View, LoginRequiredMixin):
    login_url = '/account/login/'
    
    def get(self, request, id, *args, **kwargs):
        customer = Customer.objects.get(seller=request.user, id=id)
        customerChnageinfoform = CustomerChangeInfoForm(user=request.user, initial={
            'full_name': customer.full_name,
            'phone_number': customer.phone_number,
            'address': customer.address,
        })
        context = {
            'customer': customer,
            'customerChnageinfoform': customerChnageinfoform
        }
        return render(request, "credit/customer.html", context)
    
    def post(self, request, id, *args, **kwargs):
        print(request.POST)
        if 'change-user-info' in request.POST:
            print("OOOOKKKK")
            customer = Customer.objects.get(seller=request.user, id=id)
            customerChnageinfoform = CustomerChangeInfoForm(request.POST, user=request.user, current_customer= customer)
            if customerChnageinfoform.is_valid():
                customer.full_name = request.POST.get('full_name')
                customer.phone_number = request.POST.get('phone_number')
                customer.address = request.POST.get('address')
                customer.save()
                return redirect('customer', id=customer.id)
            else:
                context = {
                    'customer': customer,
                    'customerChnageinfoform': customerChnageinfoform
                }
                return render(request, "credit/customer.html", context)
        if request.POST.get('send-message-sms'):
            pass

