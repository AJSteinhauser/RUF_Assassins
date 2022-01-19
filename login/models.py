from django.db import models


# Create your models here.
class User(models.Model):
    user_id = models.AutoField(primary_key=True);
    first_name = models.CharField(max_length=25, blank=True, null=True);
    last_name = models.CharField(max_length=25, blank=True, null=True);
    phone_num = models.PositiveIntegerField(blank=True, null=True, unique = True);
    user_pass = models.CharField(max_length=50, blank=True, null=True);
    isAdmin = models.BooleanField(default=False);
    phone_verified = models.BooleanField(default=False);
    verify_pin = models.CharField(max_length=4, blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'Users'