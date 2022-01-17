from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class User(models.Model):
    user_id = models.AutoField(primary_key=True);
    phone_number = PhoneNumberField(unique = True, null = False, blank = False);
    first_name = models.CharField(max_length=25, blank=True, null=True);
    last_name = models.CharField(max_length=25, blank=True, null=True);
    phone_num = models.PositiveIntegerField(blank=True, null=True);
    user_pass = models.CharField(max_length=50, blank=True, null=True);
    cart = models.CharField(max_length=9000000000000);
    order_history = models.JSONField(blank=True, null=True);
    isAdmin = models.BooleanField(default=False);
    class Meta:
        managed = True
        db_table = 'Users'
