from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import Customer, Factor, Products, Payment, AccountsReceivable
from .forms import CreateCustomerForm, CustomerChangeInfoForm
import jdatetime
from datetime import datetime
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
                    'id': customer.id,
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
        factor = Factor.objects.filter(seller=request.user, customer=customer, accountsReceivable=False)
        if factor.exists():
            factor_products = factor.first().products.all()
            
        
        context = {
            'customer': customer,
            'customerChnageinfoform': customerChnageinfoform,
            'factor_created' : factor.exists(),
            'factor_products' : factor_products if factor.exists() else []
        }
        return render(request, "credit/customer.html", context)
    
    def post(self, request, id, *args, **kwargs):
        if 'change-user-info' in request.POST:
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

        if "submit-product" in request.POST:
            data = {
                'name':request.POST.get('name'),
                'weight': request.POST.get('weight'),
                'price': request.POST.get('price'),
                'bio' : request.POST.get("bio")
            }
            
            product = Products.objects.create(**data)
            
            
            data['id'] = product.id
            return JsonResponse(data)
            
        if "delete-product" in request.POST:
            product_id = request.POST['product_id']
            Products.objects.get(id=product_id).delete()
   
            return JsonResponse(data={"Product":"DELETED"})

        if 'submit-factor' in request.POST:
            product_ids = request.POST.get('product_ids')
            product_ids = product_ids.split(',')
            now = jdatetime.datetime.now()
            unique_code = now.strftime('%Y%m%d%H%M%S%f')
            customer = Customer.objects.get(seller=request.user, id=id)

            total_price = 0
            total_weight = 0
            factor = Factor.objects.create(code=unique_code, seller=request.user, customer= customer)
            for p_id in product_ids:
               
                p = Products.objects.get(id=int(p_id))
                total_price += p.price
                total_weight += p.weight
                factor.products.add(p)
                
            factor.total_price = total_price
            factor.total_weight = total_weight
            factor.save()
            return JsonResponse(data={'code':factor.code})
            

        if 'delete-factor' in request.POST:
            customer = Customer.objects.get(seller=request.user, id=id)
            Factor.objects.get(seller=request.user, customer=customer, accountsReceivable=False).delete()
            return redirect('customer', id)
        

        if request.POST.get('create-account') == 'create-long':
            customer = Customer.objects.get(seller=request.user, id=id)
            customer.active_credit = True
            customer.save()

            factor = Factor.objects.get(seller=request.user, customer=customer, accountsReceivable=False)
            
            received = int(request.POST.get('long-received') or 0)
            meltedprice = int(request.POST.get('long-meltedprice'))
            date = request.POST.get('long-date').replace('/', '-')
            
            accountsReceivable = AccountsReceivable.objects.create(
                type='L',
                factor=factor
            )
            factor.accountsReceivable = True
            factor.save()
            if request.POST.get('long-borrow') == 'on':
                borrow = round((factor.total_price - received) / meltedprice, 3)
                accountsReceivable.borrow = borrow

            
            grami_remain = round((factor.total_price - received) / meltedprice , 3)

            payment = Payment.objects.create(
                payment_date = jdatetime.datetime.strptime(date, "%Y-%m-%d"),
                liquidated_price = meltedprice,
                payment_received = received,
                installment = 0,
                Account_balance_in_gram = grami_remain
            )
            accountsReceivable.payment.add(payment)
            accountsReceivable.save()
            customer.AccountsReceivable.add(accountsReceivable)
                     
            
            if grami_remain == 0:
                accountsReceivable.debit = False
                accountsReceivable.save()
                if not customer.AccountsReceivable.filter(debit=True).exists():
                    customer.active_credit = False
            else:         
                customer.active_credit = True
                customer.save()
                

            

        if request.POST.get('create-account') == 'create-grami':
            customer = Customer.objects.get(seller=request.user, id=id)
            
            factor = Factor.objects.get(seller=request.user, customer=customer, accountsReceivable=False)
            
            received = int(request.POST.get('grami-received') or 0)
            meltedprice = int(request.POST.get('grami-meltedprice'))
            date = request.POST.get('grami-date').replace('/', '-')
            installments = request.POST.get('grami-installments')
            
            accountsReceivable = AccountsReceivable.objects.create(
                type='G',
                installments = installments,
                factor=factor
            )
            factor.accountsReceivable = True
            factor.save()

            if request.POST.get('grami-borrow') == 'on':
                borrow = round((factor.total_price - received) / meltedprice, 3)
                accountsReceivable.borrow = borrow

            grami_remain = round((factor.total_price - received) / meltedprice , 3)

            payment = Payment.objects.create(
                payment_date = jdatetime.datetime.strptime(date, "%Y-%m-%d"),
                liquidated_price = meltedprice,
                payment_received = received,
                installment = 0,
                Account_balance_in_gram = grami_remain
            )

            accountsReceivable.payment.add(payment)
            accountsReceivable.save()
            customer.AccountsReceivable.add(accountsReceivable)

            if grami_remain == 0:
                accountsReceivable.debit = False
                accountsReceivable.save()
                if not customer.AccountsReceivable.filter(debit=True).exists():
                    customer.active_credit = False
                    customer.save()
            else:         
                customer.active_credit = True
                customer.save()

            return redirect('customer', id)

        if request.POST.get('create-account') == 'create-riali':
            print(request.POST)
            customer = Customer.objects.get(seller=request.user, id=id)
            factor = Factor.objects.get(seller=request.user, customer=customer, accountsReceivable=False)

            received = int(request.POST.get('riali-received') or 0) #رسید
            meltedprice = int(request.POST.get('riali-meltedprice')) #آبشده
            date = request.POST.get('riali-date').replace('/', '-')  # تاریخ
            installments = int(request.POST.get('riali-installments')) #تعداد اقساط
            interest_rates = float(request.POST.get('riali-interest_rates')) #درصد سود

            accountsReceivable = AccountsReceivable.objects.create(
                type='R',
                factor = factor,
                installments = installments,
                interest_rates = interest_rates
            )

            factor.accountsReceivable = True
            factor.save()
            riali_remain = (((installments * interest_rates) / 100 ) * (factor.total_price - received) + factor.total_price - received)
            grami_remain = None
            if request.POST.get('riali-borrow') == 'on':
                borrow = round(riali_remain / meltedprice , 2)
                accountsReceivable.borrow = borrow

            payment = Payment.objects.create(
                payment_date = jdatetime.datetime.strptime(date, "%Y-%m-%d"),
                liquidated_price = meltedprice,
                payment_received = received,
                installment = 0,
                Account_balance_in_rial = riali_remain,
                Account_balance_in_gram = 0 # NOT ADDED
            )

            accountsReceivable.payment.add(payment)
            accountsReceivable.save()
            customer.AccountsReceivable.add(accountsReceivable)

            if riali_remain == 0:
                accountsReceivable.debit = False
                accountsReceivable.save()
                if not customer.AccountsReceivable.filter(debit=True).exists():
                    customer.active_credit = False
                    customer.save()
            else:         
                customer.active_credit = True
                customer.save()

            return redirect('customer', id)

            print("riali")



