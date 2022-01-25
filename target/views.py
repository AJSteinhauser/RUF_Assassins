
from django.shortcuts import render
from django.shortcuts import redirect


from login.models import User

formatter = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"


def target(request):
    if not request.session.has_key('user_id'):
        redirect('home')
    context = {}
    obj = User.objects.get(user_id=request.session['user_id'])
    if obj.current_target: 
        target = User.objects.get(user_id=obj.current_target)
        context['first_name'] = target.first_name 
        context['last_name'] = target.last_name 
        context['portrait'] = target.phone_num
        if obj.kills_this_round == 0:
            context['first_kill'] = True

    else: 
        context['error'] = 'The game has not begun yet. Check back when round 1 starts'
    return render(request, 'target.html', context) 


def kill_report(request):
    context = {}
    context['map'] = map
    return render(request, 'kill_report.html',context)