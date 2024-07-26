from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import VirtualAccounting, UserProfiles, Profile, Balance, Development, Download, AccountUpgrade, GeneratePin
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from .services import PaystackService
import logging
from django.http import HttpResponse,HttpResponseRedirect
import random
from django.db import transaction
from django_weasyprint import WeasyTemplateView
from django.views import View
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.http import require_POST






def welcome(request):
  return render(request, "home.html")
@login_required
def notification(request):
  is_night = None
  try:
    nightmode = UserProfiles.objects.get(user=request.user)
    is_night = nightmode.night_mode
  except Exception:
    is_night = False
  return render(request, "notification.html", {"nightmode":is_night})
  
@login_required
def transaction_history(request):
  is_night = None
  try:
    nightmode = UserProfiles.objects.get(user=request.user)
    is_night = nightmode.night_mode
  except Exception:
    is_night = False
    
  dev = Development.objects.filter(user=request.user)
  return render(request, 'transaction.html', {"nightmode":is_night, "dev": dev})




def register(request):
  #check user availability
  if request.user.is_authenticated:
    return redirect("/home")
  
  #check method
  if (request.method == "POST"):
    username = request.POST.get("username")
    phone_number = request.POST.get("phone_number")
    email = request.POST.get("email")
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    password1 = request.POST.get("password1")
    password2 = request.POST.get("password2")
    nin = request.POST.get("nin")
    if (password1) and (password1 == password2) and (len(username) >=1) and (email != "") :
      try:
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        #after will save our models let try to authenticate user so we can log in our guest
        auto_log = authenticate(username=username, password=password1)
        if auto_log is not None:
          #user is created so will log-in user
          login(request, auto_log)
          Profile.objects.create(user=auto_log, phone_number=phone_number, nin=nin)
          return redirect("/home")
        else:
          #account is created but user is not unable to login let redirect user to login page
          return redirect("/")
          
      except Exception as e:
        return render(request, "create.html", {"error":e})
    else:
      #user info is not correct let redirect user to main page
      return redirect("/create")
  return render(request, 'create.html')






def logged(request):
  #check if user is already authenticated
  if request.user.is_authenticated:
    return redirect("/home")
  
  #check method
  if request.method == "POST":
    username = request.POST.get("username")
    password = request.POST.get("password")
    auth = authenticate(username=username, password=password)
    if auth is not None:
      login(request, auth)
      return redirect("/home")
    else:
      return render(request, "login.html", {"error": "Invalid Crediential"})
  return render(request, 'login.html')
  
  
  
  
  
  
@login_required
def home(request):
  is_night = None
  funds = False
  sufficient = False
  pin = False
  message = ""
  success = ""
  try:
    uprades = request.GET.get("upgrade")
    if uprades == "true":
      funds = True
      message = "Successful Upgrade to Vendor"
      success = "Successful"
      
    else:
      print("wrong parameter")
  except Exception:
    print("Not Allowed")
    
  try:
    suff = request.GET.get("sufficient")
    if suff == "false":
      sufficient = True
      message = "Insufficient Fund please add fund"
      success = "ERROR!!"
      
    else:
      print("wrong parameter")
  except Exception:
    print("Not Allowed")
    
    
  try:
    pi = request.GET.get("pwd")
    if pi == "false":
      pin = True
      message = "Incorrect Password please try again"
      success = "ERROR!!"
      
    else:
      print("wrong parameter")
  except Exception:
    print("Not Allowed")
  try:
    balance = Balance.objects.get(user=request.user)
  except Exception as e:
    Balance.objects.create(user=request.user, balance=2000)
    balance = Balance.objects.get(user=request.user)
      
  try:
    nightmode = UserProfiles.objects.get(user=request.user)
    is_night = nightmode.night_mode
  except Exception:
    is_night = False
    
  try:
    is_upgrade, create = AccountUpgrade.objects.get_or_create(user=request.user)
  except Exception as e:
    return HttpResponse("Models Not Exist")
  if request.method == "POST":
    user = request.user
    pin = request.POST.get("pin")
    try:
      my_model_instance, created = GeneratePin.objects.get_or_create(user=user)
      if my_model_instance.pin == pin:
        if balance.balance >= 1000:
          with transaction.atomic():
            # Deduct balance
            balance.balance -= 1000
            balance.save()
          try:
            myup, created = AccountUpgrade.objects.get_or_create(user=user)
            myup.upgrade = True
            myup.save()
            message = "Account Successful Upgrade!!"
            return redirect("/home?upgrade=true")
          except Exception as e:
            return HttpResponse("User Models Not Exist")
        else:
          success = "ERROR!!"
          message = "Insufficient Balance add funds and try again"
          return redirect("/home?sufficient=false")
      else:
        message = "Incorrect Password please try again"
        return redirect("/home?pwd=false")

    except MyModel.DoesNotExist:
      # Handle case where MyModel does not exist
      return HttpResponse("User model does not exist")
    except Exception as e:
      # Handle other exceptions
      return HttpResponse(f"An error occurred: {str(e)}")
  return render(request, "dashboard.html", {"nightmode":is_night, "balance": balance, "upgrade": is_upgrade, "fund": funds, "success": success, "message": message, "sufficient":sufficient, "pin":pin})
  






logger = logging.getLogger(__name__)
@login_required
def generate_virtual_account(request):
    user = request.user
    paystack_service = PaystackService()  # Create an instance of the service

    try:
        virtual_account_data = paystack_service.generate_virtual_account(user)
        if 'account_number' in virtual_account_data and 'bank' in virtual_account_data and 'reference' in virtual_account_data:
            VirtualAccounting.objects.create(
                user=user,
                account_number=virtual_account_data['account_number'],
                bank_name=virtual_account_data['bank']['name'],
                order_ref=virtual_account_data['reference']
            )
            return redirect('/home')  # Replace '/home' with the actual success page URL
        else:
            logger.debug(e)
            logger.error(f"Invalid response data: {virtual_account_data}")
            print(e)
            return HttpResponse("Failed to create virtual account. Invalid response data.",e)  # Provide a user-friendly error 
    except Exception as e:
        logger.error(f"Failed to create virtual account: {e}")
        logger.debug(e)
        print(e)
        return HttpResponse("An error occurred.")  # Provide a user-friendly error







def push_out(request):
  logout(request)
  return redirect("/accounts/login")
  
@login_required
def night_mode(request):
    try:
        # Check if the user profile exists
        user_profile = UserProfiles.objects.get(user=request.user)
        # Toggle the night_mode field
        user_profile.night_mode = not user_profile.night_mode
        user_profile.save()
        return redirect("/home")
    except UserProfiles.DoesNotExist:
        try:
            # If user profile does not exist, create one
            UserProfiles.objects.create(user=request.user, night_mode=True)
            return redirect("/home")
        except Exception as e:
            # Handle any exception that might occur during profile creation
            return HttpResponse(f"An error occurred while creating the user profile: {e}")
    except Exception as e:
        # Handle any other exceptions
        return HttpResponse(f"An error occurred: {e}")








@login_required
def purchase_data(request):
  is_night = None
  pin = ""
  try:
    x, y = GeneratePin.objects.get_or_create(user=request.user)
    pin = x.pin
  except Exception:
    return HttpResponse("Models not exist")
  try:
    nightmode = UserProfiles.objects.get(user=request.user)
    is_night = nightmode.night_mode
  except Exception:
    is_night = False
  return render(request, "data-purchase.html", {"nightmode":is_night, "pin":pin})
  
  
@login_required
def buy_bundle(request):
    if request.method == "POST":
        try:
            # Generate a unique transaction ID
            unique = random.randint(0, 999999999999)

            # Get the current user
            user = request.user

            # Get form data
            charge = request.POST.get("amount")[1:]
            phone_number = request.POST.get("phone")
            data_amount = request.POST.get("dataType")
            dataType = request.POST.get("sme")
            service = request.POST.get("network")

            # Get user's balance
            x = Balance.objects.get(user=user)

            # Check if balance is sufficient
            if x.balance >= int(charge):
                with transaction.atomic():
                    # Deduct balance
                    x.balance -= int(charge)
                    x.save()

                    # Create Development record
                    Development.objects.create(
                        user=user,
                        balance=x,
                        charge=charge,
                        service=service,
                        amount=charge,
                        phone=phone_number,
                        data_amount=data_amount,
                        transaction_id=str(unique),
                        status=True
                    )
                x = Development.objects.filter(user=user)[::-1][0]
                return redirect(f'/myreciept/{x.id}')
            else:
                return HttpResponse('Insufficient balance')

        except Balance.DoesNotExist:
            return HttpResponse('Balance record not found')

        except Exception as e:
            return HttpResponse(f"Error occurred: {str(e)}")

    return redirect("/home")
    
    
    
    
    
    
    
    
"""
class MyReciept(View):
    def get(self, request, id, *args, **kwargs):
        x = get_object_or_404(Development, id=id)
        old_balance = x.amount + x.balance.balance
        if request.GET.get('download'):
            # Handle the PDF download
            response = WeasyTemplateResponse(
                request=request,
                template='invoice.html',
                context={
                    'date': '2024-07-22',
                    'customer_name': 'John Doe',
                    'amount': '$100'
                },
                filename='invoice.pdf'
            )
            response.render()
            pdf = response.rendered_content

            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
            return response

        # Render the initial content
        return render(request, 'reciept.html',{"reciept":x, "old":old_balance})

"""

@login_required
def myreciept(request, id):
  x = get_object_or_404(Development, id=id)
  old_balance = x.amount + x.balance.balance
  return render(request, "reciept.html", {"reciept":x, "old":old_balance})
  







class InvoicePDFView(WeasyTemplateView):
    template_name = 'invoice.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = kwargs.get('id')
        x = get_object_or_404(Development, id=id)
        old_balance = x.amount + x.balance.balance
        try:
          downloaded = Download.objects.get(user=self.request.user)
          downloaded.downloaded +=1
          downloaded.save()
          self.pdf_filename = f"reciept_pystar{downloaded.downloaded}.pdf"
        except Exception as e:
          Download.objects.create(user=self.request.user, downloaded=1)
          self.pdf_filename = f"reciept_pystar{1}.pdf"
        context['reciept'] = x
        context['old'] = old_balance
        return context
        






    
@login_required
def profile(request):
  success = ""
  #message to display in the templates
  message = ""
  #exist
  same_password = False
  #currentmatch
  old_password = False
  #to handle both sucessful and check new password with retype password 
  ischange = False
  is_password_match = False
  try:
    check = request.GET.get("ischange")
    if check == "true":
      ischange = True
      message = "Password successfully change"
      success = "Successful"
    elif check == "false":
      is_password_match  = True
      message = "New Password is not match with confirm password"
      success = "ERROR!!"
    else:
      ischange = False
  except Exception:
    print("ischange not available")
    
  try:
    check = request.GET.get("currentmatch")
    if check == "false":
      old_password = True
      message = "Password not match with the old password"
      success = "ERROR!!"
    else:
      old_password  = False
  except Exception:
    print("ischange not available")
    
  try:
    check = request.GET.get("exist")
    if check == "true":
      same_password = True
      message = "Cannot use same password"
      success = "ERROR!!"
    else:
      same_password  = False
  except Exception:
    print("ischange not available")
  try:
    profiles = Profile.objects.get(user=request.user)
  except Profile.DoesNotExist:
    profiles = None
    return HttpResponse("Models not exists")
  except Exception as e:
    return HttpResponse(f"Error occurred: {e}")
  return render(request, "profile.html", {"profile":profiles, "message": message, "ischange": ischange, "old_password": old_password, "same_password": same_password, "is_match": is_password_match, "success":success})
  
  
  
  
  
  
  
  
  
@login_required
@require_POST
def change_password(request):
    current_password = request.POST.get('current_password')
    new_password = request.POST.get('new_password')
    confirm_password = request.POST.get('confirm_password')
    user = request.user
    
    if (new_password != confirm_password) and len(new_password) >= 2:
      return redirect("/profile?ischange=false")
    
    if user.check_password(new_password):
      return redirect("/profile?exist=true")
    # Check the current password
    if not user.check_password(current_password):
        messages.error(request, "Current password is incorrect.")
        return redirect('/profile?currentmatch=false')  # Redirect to the password change page
    
    # Set and save the new password
    user.set_password(new_password)
    user.save()
    
    # Update the session to prevent logout
    update_session_auth_hash(request, user)
    
    messages.success(request, "Password changed successfully.")
    return redirect('/profile?ischange=true')  # Redirect to a success page