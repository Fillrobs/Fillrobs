# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-03 17:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0022_globalpreferences_email_on_order_completion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='globalpreferences',
            name='email_on_order_completion',
            field=models.BooleanField(default=True, help_text='When enabled, every deployment order will email the requester to let them know their order has completed, and its status.', verbose_name='Email on order completion'),
        ),
    ]
