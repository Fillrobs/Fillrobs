# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-02 22:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0042_auto_20190627_2108'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customfield',
            old_name='show_on_objects',
            new_name='show_on_servers',
        ),
    ]
