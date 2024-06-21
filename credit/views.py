from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import Customer, Factor, Products, Payment, AccountsReceivable, TextMessage
from .forms import CreateCustomerForm, CustomerChangeInfoForm
from account.form import ChangePasswordForm
import jdatetime
from django.db.models import Q
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
    
    if request.GET.get('categories[]'):
        req = dict(request.GET.lists())
        types = req['categories[]']
        query= Q()

        if types == ['None']:
            customers = Customer.objects.filter(seller=request.user).order_by('-active_credit')
            
        else:
            for type in types:
                query |= Q(AccountsReceivable__type=type)

            customers = Customer.objects.filter(query).filter(seller=request.user, AccountsReceivable__debit=True).order_by('-active_credit')
        
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
        if 'phone_number' in request.POST:
            createCustomerForm = CreateCustomerForm(request.POST, user=request.user)
            if createCustomerForm.is_valid():
                new_customer = Customer.objects.create(seller= request.user ,phone_number=request.POST.get('phone_number'))
                return redirect('customer',new_customer.id)
            else:
                context = {
                'customers' : page_obj,
                'createCustomerForm': createCustomerForm,
                }
                return render(request, "credit/index.html", context)
        

    createCustomerForm = CreateCustomerForm(user=request.user)
    changePasswordForm = ChangePasswordForm(user=request.user)    
    context = {
        'customers' : page_obj,
        'createCustomerForm': createCustomerForm,
        'pieChartInfo': all_credits(request.user),
        'changePasswordForm': changePasswordForm
    }
    return render(request, "credit/index.html", context)


class CustomerCredit(View, LoginRequiredMixin):
    login_url = '/account/login/'
    
    def get(self, request, id, *args, **kwargs):
        customer = Customer.objects.get(seller=request.user, id=id)
        accountsReceivable = customer.AccountsReceivable.all().order_by('-created')
        textMessages = customer.TextMessage.all().order_by('-sent')[:3]

        paginator = Paginator(accountsReceivable, 30)
        page_number = request.GET.get('page')
        accountsReceivable_obj = paginator.get_page(page_number)
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
            'factor_products' : factor_products if factor.exists() else [],
            'accountsReceivable' : accountsReceivable_obj,
            'Calculation_payment_percentage': Calculation_payment_percentage(customer),
            'textMessages': textMessages
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
            
        if 'send-message' in request.POST:
            body = request.POST.get('body')

            textmessage = TextMessage.objects.create(body=body)
            customer = Customer.objects.get(seller=request.user, id=id)
            customer.TextMessage.add(textmessage)
            # API SEND SMS
            return redirect('customer', id)

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
                created = date,
                type='L',
                factor=factor
            )
            factor.accountsReceivable = True
            factor.save()
            if request.POST.get('long-borrow') == 'on':
                borrow = round((factor.total_price - received) / meltedprice, 3)
                accountsReceivable.borrow = borrow

            
            grami_remain = round((factor.total_price - received) / meltedprice , 2)

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

            return redirect('customer', id)
    

        if request.POST.get('create-account') == 'create-grami':
            customer = Customer.objects.get(seller=request.user, id=id)
            
            factor = Factor.objects.get(seller=request.user, customer=customer, accountsReceivable=False)
            
            received = int(request.POST.get('grami-received') or 0)
            meltedprice = int(request.POST.get('grami-meltedprice'))
            date = request.POST.get('grami-date').replace('/', '-')
            installments = request.POST.get('grami-installments')
            
            accountsReceivable = AccountsReceivable.objects.create(
                created = date,
                type='G',
                installments = installments,
                factor=factor
            )
            factor.accountsReceivable = True
            factor.save()

            if request.POST.get('grami-borrow') == 'on':
                borrow = round((factor.total_price - received) / meltedprice, 2)
                accountsReceivable.borrow = borrow

            grami_remain = round((factor.total_price - received) / meltedprice , 2)

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
            customer = Customer.objects.get(seller=request.user, id=id)
            factor = Factor.objects.get(seller=request.user, customer=customer, accountsReceivable=False)

            received = int(request.POST.get('riali-received') or 0) #رسید
            meltedprice = int(request.POST.get('riali-meltedprice')) #آبشده
            date = request.POST.get('riali-date').replace('/', '-')  # تاریخ
            installments = int(request.POST.get('riali-installments')) #تعداد اقساط
            interest_rates = float(request.POST.get('riali-interest_rates')) #درصد سود

            accountsReceivable = AccountsReceivable.objects.create(
                created = date,
                type='R',
                factor = factor,
                installments = installments,
                interest_rates = interest_rates
            )

            factor.accountsReceivable = True
            factor.save()
            riali_remain = ((((installments * interest_rates) / 100 ) * (factor.total_price - received)) + (factor.total_price - received))
            grami_remain = round(riali_remain / meltedprice, 2)
            if request.POST.get('riali-borrow') == 'on':
                borrow = round(riali_remain / meltedprice , 2)
                accountsReceivable.borrow = borrow

            payment = Payment.objects.create(
                payment_date = jdatetime.datetime.strptime(date, "%Y-%m-%d"),
                liquidated_price = meltedprice,
                payment_received = received,
                installment = 0,
                Account_balance_in_rial = riali_remain,
                Account_balance_in_gram = grami_remain
            )

            accountsReceivable.payment.add(payment)
            accountsReceivable.save()
            customer.AccountsReceivable.add(accountsReceivable)

            if riali_remain <= 0:
                accountsReceivable.debit = False
                accountsReceivable.save()
                if not customer.AccountsReceivable.filter(debit=True).exists():
                    customer.active_credit = False
                    customer.save()
            else:         
                customer.active_credit = True
                customer.save()

            return redirect('customer', id)

        if "delete-accountReceivable" in request.POST:
            accountsReceivable_id = int(request.POST.get('id'))
            accountsReceivable = AccountsReceivable.objects.get(id=accountsReceivable_id)
            for acpayment in accountsReceivable.payment.all():
                Payment.objects.get(id=acpayment.id).delete()
            accountsReceivable.delete()
            customer = Customer.objects.get(seller=request.user, id=id)
            if not customer.AccountsReceivable.filter(debit=True).exists():
                customer.active_credit = False
                customer.save()
            return redirect('customer', id)


class CustomerRialiCreditView(View, LoginRequiredMixin):
    login_url = '/account/login/'
    
    def get(self, request, customerId, creditId, *args, **kwargs):

        customer = Customer.objects.get(seller=request.user, id=customerId)
        accountReceivable = customer.AccountsReceivable.get(id=creditId)
        payments = accountReceivable.payment.all().order_by('installment')
        context = {
            'accountReceivable': accountReceivable,
            'payments': payments
        }
        return render(request, "credit/customerRialiCredit.html", context)
    
    def post(self, request, customerId, creditId, *args, **kwargs):
        if 'debt-payment' in request.POST:
            customer = Customer.objects.get(id=customerId, seller = request.user)
            accountsReceivable = AccountsReceivable.objects.get(id=creditId)
            last_payment = accountsReceivable.payment.all().order_by('installment').last()

            recived = int(request.POST.get('received'))
            meltedprice = int(request.POST.get('meltedprice'))
            date = request.POST.get('date').replace('/', '-')

            Account_balance_in_rial = last_payment.Account_balance_in_rial - recived
            creditor = recived

            payment = Payment.objects.create(
                payment_date = date,
                liquidated_price = meltedprice,
                payment_received = recived,
                installment = last_payment.installment + 1,
                creditor = creditor,
                Account_balance_in_rial = Account_balance_in_rial
            )
            accountsReceivable.payment.add(payment)
            accountsReceivable.save()

            if payment.Account_balance_in_rial <= 0:
                    accountsReceivable.debit = False
                    accountsReceivable.save()
                    if not customer.AccountsReceivable.filter(debit=True).exists():
                        customer.active_credit = False
                        customer.save()
            else:         
                customer.active_credit = True
                customer.save()

            return redirect('riali-customer-account', customerId=customerId, creditId=creditId)

class CustomerGramiCreditView(View, LoginRequiredMixin):
    login_url = '/account/login/'
    
    def get(self, request, customerId, creditId, *args, **kwargs):
        customer = Customer.objects.get(seller=request.user, id=customerId)
        accountReceivable = customer.AccountsReceivable.get(id=creditId)
        payments = accountReceivable.payment.all().order_by('installment')
        context = {
            'accountReceivable': accountReceivable,
            'payments': payments
        }
        return render(request, "credit/customerGramiCredit.html", context)
    
    def post(self, request, customerId, creditId, *args, **kwargs):
        if 'debt-payment' in request.POST:
            customer = Customer.objects.get(id=customerId, seller = request.user)
            accountsReceivable = AccountsReceivable.objects.get(id=creditId)
            last_payment = accountsReceivable.payment.all().order_by('installment').last()


            recived = int(request.POST.get('received'))
            meltedprice = int(request.POST.get('meltedprice'))
            date = request.POST.get('date').replace('/', '-')

            creditor = round(float(recived / meltedprice), 2)

            payment = Payment.objects.create(
                payment_date = date,
                liquidated_price = meltedprice,
                payment_received = recived,
                installment = last_payment.installment + 1,
                creditor = creditor,
                Account_balance_in_gram = round(float(last_payment.Account_balance_in_gram - creditor),2)
            )

            accountsReceivable.payment.add(payment)
            accountsReceivable.save()

            if payment.Account_balance_in_gram <= 0:
                    accountsReceivable.debit = False
                    accountsReceivable.save()
                    if not customer.AccountsReceivable.filter(debit=True).exists():
                        customer.active_credit = False
                        customer.save()
            else:         
                customer.active_credit = True
                customer.save()

            return redirect('long-customer-account', customerId=customerId, creditId=creditId)

class CustomerLongCreditView(View, LoginRequiredMixin):
    login_url = '/account/login/'
    
    def get(self, request, customerId, creditId, *args, **kwargs):
        customer = Customer.objects.get(seller=request.user, id=customerId)
        accountReceivable = customer.AccountsReceivable.get(id=creditId)
        payments = accountReceivable.payment.all().order_by('installment')
     
        context = {
            'accountReceivable': accountReceivable,
            'payments': payments
        }
        return render(request, "credit/customerLongTermCredit.html", context)
    
    def post(self, request, customerId, creditId, *args, **kwargs):

        if 'debt-payment' in request.POST:
            customer = Customer.objects.get(id=customerId, seller = request.user)
            accountsReceivable = AccountsReceivable.objects.get(id=creditId)
            last_payment = accountsReceivable.payment.all().order_by('installment').last()


            recived = int(request.POST.get('received'))
            meltedprice = int(request.POST.get('meltedprice'))
            date = request.POST.get('date').replace('/', '-')

            creditor = round(float(recived / meltedprice), 2)

            payment = Payment.objects.create(
                payment_date = date,
                liquidated_price = meltedprice,
                payment_received = recived,
                installment = last_payment.installment + 1,
                creditor = creditor,
                Account_balance_in_gram = round(float(last_payment.Account_balance_in_gram - creditor),2)
            )

            accountsReceivable.payment.add(payment)
            accountsReceivable.save()

            if payment.Account_balance_in_gram <= 0:
                    accountsReceivable.debit = False
                    accountsReceivable.save()
                    if not customer.AccountsReceivable.filter(debit=True).exists():
                        customer.active_credit = False
                        customer.save()
            else:         
                customer.active_credit = True
                customer.save()

            return redirect('long-customer-account', customerId=customerId, creditId=creditId)
        
#Tools 

def all_credits(seller):
    credits = {
        "L": 0,
        "G": 0,
        "R": 0,
    }
    total = 0
    customers = Customer.objects.filter(seller=seller, active_credit=True)
    for customer in customers:
        accountsReceivablecustomer = customer.AccountsReceivable.filter(debit=True)
        for accountReceivable in accountsReceivablecustomer:
            if accountReceivable.type == 'R':
                credits[accountReceivable.type] += round(accountReceivable.payment.all().order_by('payment_date').last().Account_balance_in_rial / accountReceivable.payment.all().order_by('payment_date').last().liquidated_price,2)
            else:
                credits[accountReceivable.type] += round(accountReceivable.payment.all().order_by('payment_date').last().Account_balance_in_gram, 2)
            
    
    
    for key,value in credits.items():
        total += value
        
    credits['total'] = round(total,2)
    return credits


def Calculation_payment_percentage(customer):
    credits = customer.AccountsReceivable.all()
    data = {

    }
    for credit in credits:
        if credit.type == 'G' or credit.type == 'L':
            total_weight = credit.factor.total_weight
            last_payment = credit.payment.all().order_by('payment_date').last()

            paid = (total_weight - last_payment.Account_balance_in_gram)
            percentage = round((paid / total_weight) * 100)
            data[f'{credit.id}'] = percentage

        if credit.type == 'R':
            recived = 0
            total_weight = credit.factor.total_weight
            last_payment = credit.payment.all().order_by('payment_date').last()
            for payment in credit.payment.all():
                recived += payment.payment_received

            paid_gram = recived / last_payment.liquidated_price
            percentage = round((paid_gram / total_weight) * 100)
            data[f'{credit.id}'] = percentage
    return data