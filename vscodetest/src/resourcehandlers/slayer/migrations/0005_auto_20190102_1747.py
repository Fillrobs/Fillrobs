# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-02 17:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('slayer', '0004_auto_20180503_1800'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='slayerosbuildattribute',
            name='old_template_name',
        ),
        migrations.RemoveField(
            model_name='slayerresourcehandler',
            name='old_os_build_attributes',
        ),
    ]
