# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-09-23 21:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0075_merge_20191001_0354'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalpreferences',
            name='enable_email_verification',
            field=models.BooleanField(default=True, help_text="When enabled, a user must verify their email address via an emailed confirmation link after the user's email address is changed", verbose_name='Require User Email Verification'),
        ),
    ]
