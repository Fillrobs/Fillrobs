# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-21 16:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cscv', '0007_cittest_timeout_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='actioncittest',
            name='minimum_version_required',
            field=models.CharField(default='8.6', help_text='This setting will be used to filter components during exports.', max_length=20),
        ),
    ]