# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-14 19:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0007_auto_20171214_1845'),
    ]

    operations = [
        migrations.RenameField(
            model_name='resourcehistory',
            old_name='_service',
            new_name='_resource',
        ),
        migrations.RenameField(
            model_name='resourcehistory',
            old_name='service',
            new_name='resource',
        ),
    ]