# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-07 15:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0008_fontawesome_4to5'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.Group', verbose_name='Group'),
        ),
    ]