# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-03 00:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('azure_arm', '0024_merge_20180430_1921'),
        ('externalcontent', '0007_add_osbas_to_base_field_20180501_2319')
    ]

    operations = [
        migrations.RenameField(
            model_name='azurearmhandler',
            old_name='os_build_attributes',
            new_name='old_os_build_attributes',
        ),
    ]
