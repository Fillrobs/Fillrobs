# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-03-14 14:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0001_initial'),
        ('servicecatalog', '0009_auto_20170203_1856'),
    ]

    operations = [
        migrations.AddField(
            model_name='installpodserviceitem',
            name='config_file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='files.ConfigurationFile'),
        ),
    ]