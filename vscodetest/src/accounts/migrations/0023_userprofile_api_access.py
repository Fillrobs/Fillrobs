# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-15 17:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0022_auto_20171229_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='api_access',
            field=models.BooleanField(default=True, help_text='When enabled, grants the user permission to access the API.'),
        ),
    ]
