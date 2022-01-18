from django import forms
from .models import User
from django.db import models
from django.forms import ModelForm

class NewUserForm(forms.Form):
	first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name*'}), label="")
	last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name*'}), label="")
	phone_num = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Phone Number*'}), label="", max_length=10, min_length=10)
	user_pass = forms.CharField(widget=forms.PasswordInput(render_value=True, attrs={'placeholder': 'Password*'}), label="", max_length=30)

	
