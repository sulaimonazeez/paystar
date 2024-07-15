from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import VirtualAccounting, UserProfiles
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from .models import Profile
from .services import PaystackService
import logging
from django.http import HttpResponse

def notification(request):
  is_night = None
  try:
    nightmode = UserProfiles.objects.get(user=request.user)
    is_night = nightmode.night_mode
  except Exception:
    is_night = False
  return render(request, "notification.html", {"nightmode":is_night})
  
def transaction_history(request):
  is_night = None
  try:
    nightmode = UserProfiles.objects.get(user=request.user)
    is_night = nightmode.night_mode
  except Exception:
    is_night = False
  return render(request, 'transaction.html', {"nightmode":is_night})




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

def home(request):
  is_night = None
  try:
    nightmode = UserProfiles.objects.get(user=request.user)
    is_night = nightmode.night_mode
  except Exception:
    is_night = False
  return render(request, "dashboard.html", {"nightmode":is_night})
  

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
            return HttpResponse("Failed to create virtual account. Invalid response data.",e)  # Provide a user-friendly error message
    except Exception as e:
        logger.error(f"Failed to create virtual account: {e}")
        logger.debug(e)
        print(e)
        return HttpResponse("An error occurred.")  # Provide a user-friendly error message

def push_out(request):
  logout(request)
  return redirect("/")
  

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
