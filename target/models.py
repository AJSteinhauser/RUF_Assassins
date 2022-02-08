from django.db import models

# Create your models here.

class Kill(models.Model):
    id = models.AutoField(primary_key=True);
    killer_id = models.PositiveIntegerField(default=0);
    killer_name = models.CharField(max_length=25, blank=True, null=True);
    victim_id = models.PositiveIntegerField(default=0);
    victim_name = models.CharField(max_length=25, blank=True, null=True);
    report_time_submitted = models.DateTimeField(auto_now_add=True);
    report_kill_time = models.DateTimeField();
    lat = models.FloatField();
    long = models.FloatField();
    description = models.TextField();
    confirmed = models.BooleanField(default=False);
    
    def __str__(self):
        return self.killer_name + " 🥄 " + self.victim + " (" + str(self.id) + ")"
    