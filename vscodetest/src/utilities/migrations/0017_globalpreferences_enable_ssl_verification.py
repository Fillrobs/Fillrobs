# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-07 16:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0016_auto_20170227_2228'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalpreferences',
            name='enable_ssl_verification',
            field=models.BooleanField(default=False, help_text='When disabled, SSL certificates will not be verified when making HTTPS requests.', verbose_name='SSL Verification'),
        ),
    ]
