# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-23 11:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0002_move_services_app_objs_to_resources_app_20180201_1903'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='misc_rate',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=65, null=True),
        ),
    ]
