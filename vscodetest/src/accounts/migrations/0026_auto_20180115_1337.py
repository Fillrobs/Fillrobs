# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-15 13:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0025_auto_20180112_1837'),
    ]

    operations = [
        migrations.RenameField(
            model_name='role',
            old_name='service_actions',
            new_name='resource_actions',
        ),
    ]
