# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-09-06 00:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('azure_arm', '0043_azuremeter'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='azuremeter',
            name='_effective_date',
        ),
        migrations.AddField(
            model_name='azuremeter',
            name='effective_date',
            field=models.CharField(default='2006-01-02T15:04:05Z07:00', max_length=31),
        ),
    ]