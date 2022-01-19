
import random

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import redirect
from .forms import NewUserForm
from .models import User
from start_page.views import home
from twilio.rest import Client


def validate_signup(data):
    print(data);
    if not len(data['first']) > 0: 
        return "Please enter a first name"
    if not len(data['last']) > 0: 
        return "Please enter a last name"
    if not len(data['phone']) > 0 or len(data['phone']) > 10:
        return "Please enter a valid phone number"
    if len(data['password']) < 6: 
        return "Password must be atleast 5 characters long"
    
def generate_pin(length):
    pin = ""
    for i in range(length):
        pin = pin + str(random.randint(0, 9))
    return pin




def signup(request):
    context = {};
    if request.session.has_key('user_id'):
        return redirect(home);
    if request.method == 'POST':
        context['error'] = validate_signup(request.POST)
        obj = None;
        try:
            obj = User.objects.get(phone_num=request.POST["phone"])
            context['error'] = "There is already an account associated with this phone number"
        except: 
            obj = User(
                phone_num = request.POST["phone"],
                first_name = request.POST["first"],
                last_name = request.POST["last"], 
                user_pass = request.POST["password"],
                verify_pin = generate_pin(4)
            );
            obj.save();
        if not context['error']:
            request.session['user_id'] = obj.user_id
            request.session['not_verified'] = True
            request.session['image_not_uploaded'] = True

            return redirect(verify_pin)
    return render(request, 'signup.html', context)


def login(request):
    if request.session.has_key('user_id'):
        return redirect(home);
    if request.method == 'POST':
        a = None
    return render(request, 'login.html', {})

def logout(request):
    if request.session.has_key('user_id'):
        del request.session['user_id']
    return redirect('home')


def verify_pin(request):
    context = {}
    context['mode'] = "verifying"
    if not request.session.has_key('user_id'):
        return redirect('home')
    obj = User.objects.get(user_id=request.session['user_id'])
    if request.method == 'POST':
        if obj.verify_pin == request.POST["pin"]: 
            obj.phone_verified = True;
            obj.save()
            if request.session.has_key("not_verified"):
                del request.session["not_verified"]
            return redirect('home')
    
    account_sid = 'AC4253ac2fc098bda1942fe5a909b8588e' 
    auth_token = '617e14e9a649e8d7ca1ed0b8058ee893' 
    client = Client(account_sid, auth_token) 

    message = client.messages.create(  
                        messaging_service_sid='MGf469f3b069d1008e337e65ed3fe9a062', 
                        body=('Your pin for RUF Assassins is: ' + str(obj.verify_pin)),      
                        to='+1' + str(obj.phone_num)
                    ) 
    return render(request, 'confirm_phone.html', context)
