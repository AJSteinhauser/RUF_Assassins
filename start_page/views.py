from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return render(request, "homepage.html", {})



def rules(request):
    return render(request, "rules.html", {})