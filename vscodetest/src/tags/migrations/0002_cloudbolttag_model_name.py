# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-19 23:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cloudbolttag',
            name='model_name',
            field=models.CharField(default='server', max_length=50),
        ),
    ]
