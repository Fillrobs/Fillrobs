# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-11-13 18:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('azure_arm', '0035_merge_20180814_2045'),
    ]

    operations = [
        migrations.AddField(
            model_name='azurearmdisk',
            name='host_caching',
            field=models.CharField(choices=[('NONE', 'None'), ('READONLY', 'ReadOnly'), ('READWRITE', 'ReadWrite')], default='READONLY', max_length=20),
        ),
    ]