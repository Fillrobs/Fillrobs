# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-19 20:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0008_auto_20190415_2347'),
    ]

    operations = [
        migrations.AddField(
            model_name='taggableattribute',
            name='bidirectional_sync',
            field=models.BooleanField(default=True),
        ),
    ]
