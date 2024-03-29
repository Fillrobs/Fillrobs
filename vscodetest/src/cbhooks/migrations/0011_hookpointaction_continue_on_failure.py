# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-02-24 22:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbhooks', '0010_cloudbolthook_os_families'),
    ]

    operations = [
        migrations.AddField(
            model_name='hookpointaction',
            name='continue_on_failure',
            field=models.BooleanField(default=False, help_text='If set to continue on failure, a failure of this Orchestration Action will not impact the rest of the job.'),
        ),
    ]
