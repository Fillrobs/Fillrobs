# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-03 18:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qemu', '0005_auto_20180503_0036'),
        ('externalcontent', '0010_copy_template_name_to_osba_20180503_1658')
    ]

    operations = [
        migrations.RenameField(
            model_name='qemuosbuildattribute',
            old_name='template_name',
            new_name='old_template_name',
        ),
    ]
