# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-29 17:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicecatalog', '0018_auto_20170927_1158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceblueprint',
            name='create_service',
            field=models.BooleanField(default=True, help_text='Specify whether ordering the Blueprint should create a service or simply provision any included servers and/or run any included actions.', verbose_name='Create service'),
        ),
    ]
