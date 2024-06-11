from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from .models import Customer
import json
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
    context = {
        'customers' : page_obj
    }
    return render(request, "credit/index.html", context)



