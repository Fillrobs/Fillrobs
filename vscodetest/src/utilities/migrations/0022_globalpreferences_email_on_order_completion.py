# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-08 19:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0021_merge_20170817_1933'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalpreferences',
            name='email_on_order_completion',
            field=models.BooleanField(default=True, verbose_name='Email On Order Completion'),
        ),
    ]
