from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from target.views import add_kill_status



def home(request):
    add_kill_status(request)
    return render(request, "homepage.html", {'time': settings.ROUND_1_START})



def rules(request):
    add_kill_status(request)
    return render(request, "rules.html", {})