# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-17 22:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('azure_arm', '0007_auto_20170413_1955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='azurearmserverinfo',
            name='resource_group',
            field=models.CharField(max_length=1024),
        ),
    ]