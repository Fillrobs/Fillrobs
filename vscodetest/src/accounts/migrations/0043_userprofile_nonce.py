# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-09-13 20:43
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0042_merge_20190820_2016'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='nonce',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
