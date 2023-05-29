# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-07 15:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0036_globalpreferences_enable_cost_preview_per_env'),
    ]

    operations = [
        migrations.AlterField(
            model_name='globalpreferences',
            name='enable_cost_preview_per_env',
            field=models.BooleanField(default=True, help_text='When disabled, cost preview per environment will not be shown in the order form.', verbose_name='Show cost preview when ordering'),
        ),
    ]