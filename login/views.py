from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import NewUserForm


def signup(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/thanks/')
    else:
        form = NewUserForm()

    return render(request, 'signup.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/thanks/')
    else:
        form = NewUserForm()
    return render(request, 'login.html', {})