# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-09-18 12:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cbhooks', '0037_serveraction_condition'),
        ('servicecatalog', '0034_serviceblueprint_favorited'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceblueprint',
            name='discovery_plugin',
            field=models.ForeignKey(blank=True, help_text='A plug-in containing logic that is used to discover and sync existing Resources of the type described by this Blueprint.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='cbhooks.CloudBoltHook', verbose_name='Discovery Plug-in'),
        ),
    ]