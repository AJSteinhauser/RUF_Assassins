from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings



def home(request):
    return render(request, "homepage.html", {'time': settings.ROUND_1_START})



def rules(request):
    return render(request, "rules.html", {})