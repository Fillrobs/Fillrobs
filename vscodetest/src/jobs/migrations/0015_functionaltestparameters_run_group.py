# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-11 19:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0014_job_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='functionaltestparameters',
            name='run_group',
            field=models.BooleanField(default=False, help_text='Set to true when this job is set to run a group of tests'),
        ),
    ]
