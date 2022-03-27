
import random
import os
from time import sleep
import sys
import face_recognition
from dstructure.SCLL import SCLL
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from PIL import Image, ExifTags
from django.shortcuts import redirect
from .forms import NewUserForm
from .models import User
from target.models import Kill
from start_page.views import home
from django.conf import settings
from target.views import add_kill_status
from .helper import send_text
from datetime import datetime




def validate_signup(data):
    if not len(data['first']) > 0: 
        return "Please enter a first name"
    if not len(data['last']) > 0: 
        return "Please enter a last name"
    if not len(data['phone']) > 0 or len(data['phone']) > 10:
        return "Please enter a valid phone number"
    if len(data['password']) < 6: 
        return "Password must be atleast 5 characters long"
    if data['secret'].lower() != "coppedge":
        return "Invalid secret key"


    
    
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
    context = {}
    if (settings.ROUND_1_START - datetime.now()).total_seconds() <= 0: 
        context['error'] = "The game has already started. It's too late to sign up"
        return render(request, 'signup.html',context)
    if (settings.SIGN_UP_CLOSE - datetime.now()).total_seconds() <= 0: 
        context['error'] = "Sign ups have closed for this game."
        return render(request, 'signup.html',context)
    if request.session.has_key('user_id'):
        return redirect(home)
    if request.method == 'POST':
        context['error'] = validate_signup(request.POST)
        obj = None
        print(2)
        print(('error' in context))
        print(context['error'])
        if not context['error']:
            print(3)
            try:
                print(4)
                obj = User.objects.get(phone_num=request.POST["phone"])
                context['error'] = "There is already an account associated with this phone number"
            except:
                print(5) 
                obj = User(
                    phone_num = request.POST["phone"],
                    first_name = request.POST["first"],
                    last_name = request.POST["last"], 
                    user_pass = request.POST["password"],
                    verify_pin = generate_pin(4)
                )
                obj.save()
            if not context['error']:
                print(6)
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

def execute_admin_command(command):
    command = command.lower()
    if command == "testing":
        return "test command"
    elif command == "unconfirmed kills":
        kill_list = list(Kill.objects.all())
        string = ""
        for kill in kill_list:
            if not kill.confirmed:
                string = string + str(kill)
        return string

    elif command == "kill round 1":
        plr_list = list(User.objects.all())
        string = ""
        for plr in plr_list:
            if plr.alive:
                if plr.kills_this_round == 0:
                    string = string + str(plr)
                    obj = Kill(
                        killer_id = 1,
                        killer_name = "Spencer 🐶",
                        victim_id = plr.user_id,
                        report_time_submitted = settings.TIMEZONE.localize(datetime.now()),
                        victim_name = plr.first_name + ' ' + plr.last_name, 
                        lat = 0,
                        long = 0,
                        description = "Spencer 🐶: " + 'GRRR, GRRR, RUFFFF RUFFFF. <p class="text-center fw-lighter">' + plr.first_name + ' failed to get a kill before the end of round 1</p>', 
                        confirmed = True
                    )
                    obj.save()
                    plr.alive = False;
                    plr.save()
                    send_text(plr.phone_num,"You have been eliminated for failing to kill 1 target before friday at 11:59")
        return string
    elif command == "confirm playing":
        plr_list = list(User.objects.all())
        for plr in plr_list:
            if plr.phone_verified and plr.image_uploaded: 
                send_text(plr.phone_num,"Reminder: Assassins starts friday night, you are signed up to play")
    elif command == "delete unverified accounts":
        plr_list = list(User.objects.all())
        for plr in plr_list:
            if not plr.phone_verified or not plr.image_uploaded: 
                print(plr);
                send_text(plr.phone_num, "Your accound has been deleted for failing to confirm phone# or uploading image by the end of sign-ups");
                plr.delete();
    elif command == "check unverified accounts":
        plr_list = list(User.objects.all())
        s = "Unverified accounts:\n"
        for plr in plr_list:
            if not plr.phone_verified or not plr.image_uploaded: 
                print(plr);
                s = s + str(plr) + "\n"
        return s;
    elif command == "verify accounts reminder":
        plr_list = list(User.objects.all())
        for plr in plr_list:
            if not plr.phone_verified: 
                send_text(plr.phone_num, "Your account phone number must be verifed by" + settings.ROUND_1_START.strftime("%A, %B %-d at %I:%M %p") + "else your account will be deleted ajsteinhauser.org/verify")
            if not plr.image_uploaded:
                send_text(plr.phone_num, "You must upload a profile image by" + settings.ROUND_1_START.strftime("%A, %B %-d at %I:%M %p") + "else your account will be deleted. ajsteinhauser.org/profileimage")
    elif command == "clear current kills":
        plr_list = list(User.objects.all())
        for plr in plr_list:
            if plr.alive:
                plr.kills_this_round = 0;
                plr.save();
        return "Kills cleared"
    
    elif command == "assign targets":
        plr_list = list(User.objects.all())
        newlist = []
        for plr in plr_list:
            if plr.alive:
                newlist.append(plr)
        plr_list = newlist
        length = len(plr_list)
        circle = SCLL()
        while len(plr_list) > 0:
            randomplr = plr_list.pop(random.randint(0, len(plr_list)-1))
            circle.insert(randomplr)
        circle = circle.root
        target_list = ""
        print(length + 1)
        for i in range(0,length + 1):
            target_list = target_list + str(circle.data) + "->"
            circle.data.current_target = circle.next.data.user_id
            circle.data.save()
            circle = circle.next
        return target_list
    elif command == "start game":
        plr_list = list(User.objects.all())
        for plr in plr_list:
            send_text(plr.phone_num, "You can see your targets now. Go to ajsteinhauser.org/target to find out who you have. The game does not start until midnight")
    elif command[0:8] == "message:":
        plr_list = list(User.objects.all())
        for plr in plr_list:
            send_text(plr.phone_num,command[8:])
        return "sent" + command[8:]
    elif command == "check list":
        plr_list_count = len(list(User.objects.all()))
        initial_player = None;
        plrlist = list(User.objects.all())
        for plr in plrlist:
            if plr.alive:
                initial_player = plr
                break
        current_player = User.objects.get(user_id=initial_player.current_target)
        target_list = str(initial_player) + "->\n"
        count = 1
        while (current_player != initial_player) or count > plr_list_count:
            target_list = target_list + str(current_player) + "->\n"
            current_player = User.objects.get(user_id=current_player.current_target)
            count = count + 1
        
        return (str(plr_list_count) + " == " + str(count) + "\nList:\n" + target_list);

    elif command[0:5] == "find:":
        phonenumber = command[5:]
        try:
            obj = User.objects.get(phone_num=phonenumber)
            return str(obj)
        except:
            return phonenumber + " player not found"
    else:
        return "Error: no command executed"
    return "Command excuted successfully"

def game_admin(request):
    context = {}
    if not request.session.has_key('user_id'):
        return redirect(home)
    obj = User.objects.get(user_id=request.session['user_id'])
    if not obj.isAdmin:
        return redirect('home')
    if request.method == 'POST':
        context['error'] = execute_admin_command(request.POST['command'])
    return render(request, 'admin_page.html', context)