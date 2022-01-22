from django.contrib import admin
from .models import User


class Useradmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')


admin.site.register(User)

# Register your models here.
