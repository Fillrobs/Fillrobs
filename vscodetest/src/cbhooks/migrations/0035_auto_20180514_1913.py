# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-14 19:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cbhooks', '0034_merge_20180117_1435'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cloudbolthook',
            options={'verbose_name': 'CloudBolt Plug-in'},
        ),
        migrations.AlterModelOptions(
            name='emailhook',
            options={'verbose_name': 'Email Hook'},
        ),
        migrations.AlterModelOptions(
            name='flowhook',
            options={'verbose_name': 'External Flow'},
        ),
        migrations.AlterModelOptions(
            name='remotescripthook',
            options={'verbose_name': 'Remote Script'},
        ),
        migrations.AlterModelOptions(
            name='webhook',
            options={'verbose_name': 'Webhook'},
        ),
    ]
