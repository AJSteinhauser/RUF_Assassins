

from datetime import datetime
from re import M
import pytz
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from .models import Kill


from login.models import User

formatter = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"


def target(request):
    if not request.session.has_key('user_id'):
        redirect('home')
    context = {}
    obj = User.objects.get(user_id=request.session['user_id'])
    if obj.current_target:
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
        context['error'] = 'The game has not begun yet. Check back when round 1 starts'
    return render(request, 'target.html', context) 


def kill_report(request):
    if not request.session.has_key('user_id'):
        return redirect('home')
    context = {}
    context['map'] = map
    userobj = User.objects.get(user_id=request.session['user_id'])
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
            confirmed = True
        )
        obj.save()
    return render(request, 'kill_report.html',context)



def stats(request):
    context = {}
    kill_list = list(Kill.objects.all().order_by('-report_time_submitted'))
    plr_list = list(User.objects.all().order_by('-total_kills'))
    
    context['flipper'] = 0
    context['round_end'] = "Sunday, March 16, 2022"
    context['round_end_togo'] = 8

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
    context.update({'leaderboard':leaderboard})    
    context.update({'kill_stream':kill_stream})    
    return render(request, 'live_stats.html',context)
