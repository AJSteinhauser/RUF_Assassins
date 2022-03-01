
import random
import os
from time import sleep
import sys
import face_recognition
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from PIL import Image, ExifTags
from django.shortcuts import redirect
from .forms import NewUserForm
from .models import User
from start_page.views import home
from django.conf import settings
from target.views import add_kill_status
from .helper import send_text



def validate_signup(data):
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

def verify_pin(request):
    add_kill_status(request)
    if not request.session.has_key('user_id'):
        return redirect('home')
    context = {}
    context['mode'] = "verifying"
    obj = User.objects.get(user_id=request.session['user_id'])
    if obj.phone_verified:
        return redirect('home')
    if request.method == 'POST':
        if obj.verify_pin == request.POST["pin"]:
            obj.phone_verified = True
            obj.save()
            if request.session.has_key("not_verified"):
                del request.session["not_verified"]
            return redirect('uploadimage')
        else: 
            context['error'] = "Incorrect pin, new pin being sent"
    try: 
        send_text(obj.phone_num, 'Your pin is: ' + str(obj.verify_pin))
    except:
        context['error'] = "active"
        context['reload'] = "active"
    return render(request, 'confirm_phone.html', context)

def signup(request):
    add_kill_status(request)
    if request.session.has_key('user_id'):
        return redirect(home)
    context = {}
    if request.method == 'POST':
        context['error'] = validate_signup(request.POST)
        obj = None
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
            )
            obj.save()
        if not context['error']:
            request.session['user_id'] = obj.user_id
            request.session['not_verified'] = True
            request.session['image_not_uploaded'] = True

            return redirect(verify_pin)
    return render(request, 'signup.html', context)

def login(request):
    add_kill_status(request)
    if request.session.has_key('user_id'):
        return redirect(home)
    context = {}
    if request.method == 'POST':
        try:
            obj = User.objects.get(phone_num=request.POST["phone"])
            if request.POST['pass'] == obj.user_pass: 
                request.session['user_id'] = obj.user_id
                if not obj.image_uploaded:
                    request.session['image_not_uploaded'] = True
                if not obj.phone_verified:
                    request.session['not_verified'] = True
                return redirect(home)
            context['error'] = 'No account with that phone number and password exists'
        except:
            context['error'] = 'No account with that phone number & password exists'
    return render(request, 'login.html', context)

def logout(request):
    add_kill_status(request)
    if request.session.has_key('user_id'):
        del request.session['user_id']
    if request.session.has_key('not_verified'):
        del request.session['not_verified']
    if request.session.has_key('image_not_uploaded'):
        del request.session['image_not_uploaded']
    return redirect('home')

def fix_image(image,filepath):
    
    image = Image.open(image)
    try:
        
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        exif = image._getexif()

        if exif[orientation] == 3:
            image=image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image=image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image=image.rotate(90, expand=True)

    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass
    image = image.convert('RGB')
    image.save(filepath,format="jpeg",quality=20)
    print(filepath)
    image.close()
    

def upload_image(request):
    add_kill_status(request)
    if not request.session.has_key('user_id'):
        return redirect(home)
    if not request.session.has_key('image_not_uploaded'):
        return redirect(home)
    context = {}
    context['mode'] = "verifying"
    if request.method == 'POST':
        #sleep(5)
        obj = User.objects.get(user_id=request.session['user_id'])
        try: 

            fix_image(request.FILES.get('img'),settings.MEDIA_ROOT + "/" + str(obj.phone_num) + ".jpeg")
            face_recog = face_recognition.load_image_file(settings.MEDIA_ROOT + "/" + str(obj.phone_num) + ".jpeg")
            face_locations = face_recognition.face_locations(face_recog,1)
        except Exception as e:
            print(e.args)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #print(exc_type, fname, exc_tb.tb_lineno)
            sys.stderr.write("Next line\n")
            sys.stderr.write(str(exc_type))
            sys.stderr.write(str(fname))
            sys.stderr.write(str(exc_tb.tb_lineno))
            context['error'] = "Something went wrong. Please try again"
            return render(request, 'upload_image.html', context)
        if len(face_locations) > 1:
            context['error'] = "There are too many people in this image. Please use images of you alone."
            context['image'] = str(obj.phone_num)
            return render(request, 'upload_image.html', context)
        elif len(face_locations) == 0: 
            context['error'] = "No people detected. Try another image, low lighting images can effect results"
            context['image'] = str(obj.phone_num)
            return render(request, 'upload_image.html', context)
        obj.image_uploaded = True
        obj.save()
        if request.session.has_key('image_not_uploaded'):
            del request.session['image_not_uploaded']
        return redirect('home')
    return render(request, 'upload_image.html', context)