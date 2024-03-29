# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-02-05 19:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0051_merge_20190102_1954'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalpreferences',
            name='enable_original_password_field',
            field=models.BooleanField(default=True, help_text="When enabled, changing a user's password requires entering their previous password", verbose_name='Original Password Verification'),
        ),
        migrations.AlterField(
            model_name='globalpreferences',
            name='enable_password_toggle',
            field=models.BooleanField(default=False, help_text='When enabled, users will be able to unmask passwords in any form field, if they have the appropriate rights to do so.', verbose_name='Password Toggle'),
        ),
    ]
