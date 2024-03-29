# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-23 16:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0015_functionaltestparameters_run_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('QUEUED', 'Queued'), ('RUNNING', 'Running'), ('SUCCESS', 'Completed successfully'), ('WARNING', 'Completed with warnings'), ('FAILURE', 'Completed with errors'), ('TO_CANCEL', 'In cancellation process'), ('CANCELED', 'Canceled by user')], db_index=True, default='PENDING', max_length=10, verbose_name='Job status'),
        ),
    ]
