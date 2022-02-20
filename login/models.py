from email.policy import default
from django.db import models


# Create your models here.
class User(models.Model):
    user_id = models.AutoField(primary_key=True);
    first_name = models.CharField(max_length=25, blank=True, null=True);
    last_name = models.CharField(max_length=25, blank=True, null=True);
    phone_num = models.PositiveIntegerField(blank=True, null=True, unique = True);
    user_pass = models.CharField(max_length=50, blank=True, null=True);
    isAdmin = models.BooleanField(default=False);
    image_uploaded = models.BooleanField(default=False);
    phone_verified = models.BooleanField(default=False);
    verify_pin = models.CharField(max_length=4, blank=True, null=True);
    pins_sent = models.PositiveIntegerField(default=0);
    current_target = models.PositiveIntegerField(blank=True, null=True);
    kills_this_round = models.PositiveIntegerField(default=0);
    alive = models.BooleanField(default=True);
    kill_verifying = models.BooleanField(default=False);
    death_pending = models.BooleanField(default=False);
    total_kills = models.PositiveIntegerField(default=0);
    class Meta:
        managed = True
        db_table = 'Users'
    def __str__(self):
        return self.first_name + " " + self.last_name + " (" + str(self.user_id) + ")"
    