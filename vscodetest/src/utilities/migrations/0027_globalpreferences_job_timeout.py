# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-17 17:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0026_auto_20171016_1648'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalpreferences',
            name='job_timeout',
            field=models.IntegerField(default=3600, help_text='The default number of seconds any job can run.', verbose_name='Default job timeout'),
        ),
    ]
