# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-16 23:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vcloud_director', '0009_vcdserverinfo_vapp_href'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vcdhandler',
            name='os_build_attributes',
        ),
    ]
