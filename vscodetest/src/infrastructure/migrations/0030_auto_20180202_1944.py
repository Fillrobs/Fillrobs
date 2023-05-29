# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-02 19:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0029_merge_20180129_1956'),
        ('resources',
         '0002_move_services_app_objs_to_resources_app_20180201_1903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcepoolvalueset',
            name='resource',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='resources.Resource'),
        ),
        migrations.AlterField(
            model_name='server',
            name='resource',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='resources.Resource'),
        ),
    ]
