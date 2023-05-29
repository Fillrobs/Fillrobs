# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-28 22:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbhooks', '0015_auto_20170303_2309'),
        ('accounts', '0010_auto_20170420_0048'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='server_actions',
            field=models.ManyToManyField(blank=True, related_name='roles', to='cbhooks.ServerAction'),
        ),
        migrations.AddField(
            model_name='role',
            name='service_actions',
            field=models.ManyToManyField(blank=True, related_name='roles', to='cbhooks.ServiceAction'),
        ),
    ]