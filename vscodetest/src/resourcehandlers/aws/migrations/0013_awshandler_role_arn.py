# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2020-03-17 08:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aws', '0012_merge_20190315_2236'),
    ]

    operations = [
        migrations.AddField(
            model_name='awshandler',
            name='role_arn',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]