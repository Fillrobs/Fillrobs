# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-02 19:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('containerorchestrators', '0004_auto_20180108_1734'),
        ('resources',
         '0002_move_services_app_objs_to_resources_app_20180201_1903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='containerresource',
            name='resource',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='container_resources', to='resources.Resource'),
        ),
    ]
