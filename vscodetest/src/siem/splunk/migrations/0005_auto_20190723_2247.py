# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-23 22:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('splunk', '0004_remove_splunkconf_timezone'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='splunkconf',
            name='remote_password',
        ),
        migrations.RemoveField(
            model_name='splunkconf',
            name='remote_splunk_bin_path',
        ),
        migrations.RemoveField(
            model_name='splunkconf',
            name='remote_username',
        ),
    ]