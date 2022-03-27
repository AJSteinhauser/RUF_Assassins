

from datetime import datetime
import pytz
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from .models import Kill
from login.helper import send_text



from login.models import User

formatter = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"


def target(request):
    add_kill_status(request)
    if not request.session.has_key('user_id'):
        return redirect('home')
    context = {}
    obj = User.objects.get(user_id=request.session['user_id'])
    if obj.current_target and obj.alive:
        if not obj.death_pending:
            if not obj.kill_verifying:
                target = User.objects.get(user_id=obj.current_target)
                context['first_name'] = target.first_name 
                context['last_name'] = target.last_name 
                context['portrait'] = target.phone_num
                if obj.kills_this_round == 0:
                    context['first_kill'] = True
            else: 
                context['error'] = 'Waiting on your target to verify the kill'
        else:
            context['error'] = 'You must respond to kill report before submitting kill'
    else: 
        if not obj.alive:
            context['error'] = "You have been eliminated from the game"
        else:
            context['error'] = 'The game has not begun yet. Check back when round 1 starts'
    return render(request, 'target.html', context) 


def add_kill_status(request):
    if request.session.has_key('user_id'):
        try: 
            obj = User.objects.get(user_id=request.session['user_id'])
        except: 
            del request.session['user_id']
            return
        if obj.kill_verifying:
            request.session['wait_for_verify'] = True
        else: 
            if request.session.has_key("wait_for_verify"):
                del request.session['wait_for_verify']
        if obj.death_pending:
                request.session['verify_kill'] = True
        else: 
            if request.session.has_key("verify_kill"):
                del request.session['verify_kill']
    else:
        if request.session.has_key("verify_kill"):
            del request.session['verify_kill']
        if request.session.has_key("wait_for_verify"):
            del request.session['wait_for_verify']

def kill_report(request):
    add_kill_status(request)
    if not request.session.has_key('user_id'):
        return redirect('home')
    if (datetime.now() - settings.ROUND_1_START).total_seconds() <= 0:
        return redirect('home')
    context = {}
    context['map'] = map
    userobj = User.objects.get(user_id=request.session['user_id'])
    if userobj.kill_verifying:
        return redirect('home')
    if not userobj.alive: 
        return redirect('home')
    if request.method == 'POST':
        victimobj = User.objects.get(user_id=userobj.current_target)
        timezone = pytz.timezone("US/Eastern")
        obj = Kill(
            killer_id = userobj.user_id,
            killer_name = userobj.first_name + ' ' + userobj.last_name,
            victim_id = victimobj.user_id,
            report_time_submitted = timezone.localize(datetime.now()),
            victim_name = victimobj.first_name + ' ' + victimobj.last_name, 
            lat = request.POST['lat'],
            long = request.POST['long'],
            description = request.POST['description'], 
            confirmed = False
        )
        obj.save()
        userobj.kill_verifying = True;
        victimobj.death_pending = True;
        userobj.save();
        victimobj.save();
        request.session['wait_for_verify'] = True;
        send_text(victimobj.phone_num,"A kill report has been submitted about you, please respond ASAP to keep the game moving ajsteinhauser.org")
        return redirect('home');
    return render(request, 'kill_report.html',context)

def confirm_kill_page(request):
    add_kill_status(request)
    if not request.session.has_key('user_id'):
        return redirect('home')
    userobj = User.objects.get(user_id=request.session['user_id'])
    if not userobj.death_pending: 
        return redirect('home')
    context = {}
    return render(request, 'confirm_kill.html',context)

def confirm_kill_agree(request):
    add_kill_status(request)
    if not request.session.has_key('user_id'):
        return redirect('home')
    userobj = User.objects.get(user_id=request.session['user_id'])
    if userobj.death_pending:
        userobj.death_pending = False;
        userobj.alive = False;
        plr_list = list(User.objects.all().order_by('-total_kills'))
        targetPlayer = None;
        for plr in plr_list: 
            if plr.current_target == userobj.user_id: 
                targetPlayer = plr;
                break;
        print(targetPlayer.user_id)
        print(userobj.user_id)
        killobj = Kill.objects.get(killer_id = targetPlayer.user_id, victim_id = userobj.user_id)
        killobj.confirmed = True;
        targetPlayer.kill_verifying = False;
        targetPlayer.kills_this_round = targetPlayer.kills_this_round + 1;
        targetPlayer.total_kills = targetPlayer.total_kills + 1;
        targetPlayer.current_target = userobj.current_target;
        killobj.save();
        targetPlayer.save();
        userobj.save();
        send_text(targetPlayer.phone_num, userobj.first_name + " " + userobj.last_name + " has confirmed the kill. You have been assigned a new target, details on the website.")
    return redirect('home')

def confirm_kill_deny(request):
    add_kill_status(request)
    context = {}
    if not request.session.has_key('user_id'):
        return redirect('home')
    userobj = User.objects.get(user_id=request.session['user_id'])
    if userobj.death_pending:
        userobj.death_pending = False;
        targetPlayer = None;
        plr_list = list(User.objects.all().order_by('-total_kills'))
        for plr in plr_list: 
            if plr.current_target == userobj.user_id: 
                targetPlayer = plr;
                break;
        killobj = Kill.objects.get(killer_id = targetPlayer.user_id, victim_id = userobj.user_id)
        killobj.delete()
        targetPlayer.kill_verifying = False;
        targetPlayer.save();
        userobj.save();
        send_text(targetPlayer.phone_num, userobj.first_name + " " + userobj.last_name + " has denied the kill. If this was an error submit another kill report otherwise get in contact with us")
    return redirect('home')


def leaderboard(request):
    add_kill_status(request)
    context = {}
    plr_list = list(User.objects.all().order_by('-total_kills'))
    leaderboard = []
    i = 0
    for plr in plr_list:
        if plr.total_kills > 0:
            leader_info = {
                'name' : plr.first_name + " " + plr.last_name,
                'kills' : plr.total_kills,
                'placement' : i + 1
            }
            if not plr.alive:
                leader_info['name'] = "<strike>" + leader_info['name'] + "</strike><i> (Deceased)</i>"
            leaderboard.append(leader_info)
            i = i + 1
    context.update({'leaderboard':leaderboard})
    return render(request, 'leaderboard.html',context)

def kill_feed(request):
    add_kill_status(request)
    context = {}
    kill_list = list(Kill.objects.all().order_by('-report_time_submitted'))
    kill_stream = []
    
    for obj in kill_list:
        if obj.confirmed:
            then = obj.report_time_submitted.replace(tzinfo=None)
            now = datetime.now()
            duration = (now - then).total_seconds()
            killer_info = {
                'killer' : obj.killer_name,
                'victim' : obj.victim_name,
                'desc' : obj.killer_name + ": " + obj.description,
                'days' : int(divmod(duration, 3600 * 24)[0]),
                'hours' : int(divmod(duration, 3600)[0]),
                'mins' : int(divmod(duration, 60)[0])
            }
            kill_stream.append(killer_info)
    context.update({'kill_stream':kill_stream})  
    return render(request, 'kill_feed.html',context)  



def stats(request):
    add_kill_status(request)
    context = {}
    kill_list = list(Kill.objects.all().order_by('-report_time_submitted'))
    plr_list = list(User.objects.all().order_by('-total_kills'))

    
    
    if (datetime.now() - settings.ROUND_1_START).total_seconds() <= 0: 
        context["message"] = "Game has not started yet.\n Check back here after " + settings.ROUND_1_START.strftime("%A, %B %-d at %I:%M %p")
        return render(request, 'live_stats.html',context)
    if len(kill_list) < 1: 
        context["message"] = "There have been no kills yet. Check back here after first blood."
        return render(request, 'live_stats.html',context)
    context['round_end'] = settings.ROUND_1_END.strftime("%A, %B %-d at %I:%M %p")
    context['round_end_togo'] = max(0,int(divmod((settings.ROUND_1_END - datetime.now()).total_seconds(), 3600)[0]))

    plr_counter = 0;
    kill_leader_count = -1
    kill_leader_name = ""
    kill_leader_phone = ""
    leaderboard = []
    i = 0;
    for plr in plr_list:
        if plr.total_kills > kill_leader_count:
            kill_leader_count = plr.total_kills
            kill_leader_name = plr.first_name + " " + plr.last_name
            kill_leader_phone = plr.phone_num
        if plr.alive: 
            plr_counter = plr_counter + 1
        if i < 5:
            leader_info = {
                'name' : plr.first_name + " " + plr.last_name,
                'kills' : plr.total_kills,
                'placement' : i + 1
            }
            if not plr.alive:
                leader_info['name'] = "<i><strike>" + leader_info['name'] + "</strike></i>"
            leaderboard.append(leader_info)
            i = i + 1

    context['kill_leader_name'] = kill_leader_name
    context['kill_leader_portrait'] = kill_leader_phone
    context['kill_leader_count'] = kill_leader_count
    context['players_active'] = plr_counter
    
    i = 0;
    context['death_points'] = []
    kill_stream = []
    for obj in kill_list:
        if obj.confirmed:
            if obj.lat != 0:
                location = {
                    'lat' : obj.lat,
                    'long' : obj.long,
                } 
                context['death_points'].append(location)
            if i == 0: 
                context['recent_kill_portrait'] = User.objects.get(user_id=obj.victim_id).phone_num
                context['recent_kill_name'] = obj.victim_name
                death_time = obj.report_time_submitted.replace(tzinfo=None)
                then = settings.ROUND_1_START
                duration = (death_time - then).total_seconds()
                recent_death_time = {
                    'days' : int(divmod(duration, 3600 * 24)[0]),
                    'hours' : int(divmod(duration, 3600)[0]),
                    'mins' : int(divmod(duration, 60)[0])
                }
                context['recent_death_time'] = recent_death_time
            if i < 6:
                then = obj.report_time_submitted.replace(tzinfo=None)
                now = datetime.now()
                duration = (now - then).total_seconds()
                killer_info = {
                    'killer' : obj.killer_name,
                    'victim' : obj.victim_name,
                    'days' : int(divmod(duration, 3600 * 24)[0]),
                    'hours' : int(divmod(duration, 3600)[0]),
                    'mins' : int(divmod(duration, 60)[0])
                }
                kill_stream.append(killer_info)
                i = i + 1
    if i <= 0:
        context["message"] = "There have been no kills yet. Check back here after first blood."
    context.update({'leaderboard':leaderboard})    
    context.update({'kill_stream':kill_stream})    
    return render(request, 'live_stats.html',context)
