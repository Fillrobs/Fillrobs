# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-23 16:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resourcehandlers', '0009_auto_20171212_1729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcenetwork',
            name='name',
            field=models.CharField(help_text='Display name for the network. Not used in any programmatic fashion and can be changed safely.', max_length=256),
        ),
        migrations.AlterField(
            model_name='resourcenetwork',
            name='network',
            field=models.CharField(help_text='Identifying name/ID of the network. Used as an identifier and should not be changed.', max_length=256),
        ),
    ]