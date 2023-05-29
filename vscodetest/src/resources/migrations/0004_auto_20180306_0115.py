# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-06 01:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0030_auto_20180202_1944'),
        ('resources', '0003_resourcetype_list_view_columns'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='power_off_scheduled_times',
            field=models.ManyToManyField(blank=True, help_text='ScheduledTimes at which the Resource should be powered off.', related_name='resources_to_power_off', to='infrastructure.ScheduledTime'),
        ),
        migrations.AddField(
            model_name='resource',
            name='power_on_scheduled_times',
            field=models.ManyToManyField(blank=True, help_text='ScheduledTimes at which the Resource should be powered on.', related_name='resources_to_power_on', to='infrastructure.ScheduledTime'),
        ),
    ]
