# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-13 20:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbhooks', '0020_auto_20171004_2003'),
    ]

    operations = [
        migrations.AddField(
            model_name='webhook',
            name='custom_headers',
            field=models.TextField(
                blank=True, default='',
            help_text="JSON object where keys are HTTP header names and values are header values. Ex. {'user-agent': 'my-app/0.0.1'}"),
        ),
    ]