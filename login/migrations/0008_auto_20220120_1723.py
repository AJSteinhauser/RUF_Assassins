# Generated by Django 3.1.5 on 2022-01-20 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0007_remove_user_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='current_target',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='pins_sent',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
