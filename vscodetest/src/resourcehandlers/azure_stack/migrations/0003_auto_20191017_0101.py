# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-10-17 01:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('azure_stack', '0002_auto_20170822_1512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='azurestackhandler',
            name='metadata_endpoint',
            field=models.CharField(max_length=1024, verbose_name='Metadata Endpoint'),
        ),
    ]