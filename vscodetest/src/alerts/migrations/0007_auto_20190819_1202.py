# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-08-19 12:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0006_auto_20190815_2002'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='emailalertchannel',
            options={'verbose_name': 'Email'},
        ),
        migrations.AlterModelOptions(
            name='slackalertchannel',
            options={'verbose_name': 'Slack'},
        ),
    ]
