# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-02 20:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0039_auto_20190618_2147'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='view_initial_tour',
            field=models.BooleanField(default=True),
        ),
    ]
