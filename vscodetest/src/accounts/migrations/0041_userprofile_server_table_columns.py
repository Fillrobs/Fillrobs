# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-07 22:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0040_userprofile_catalog_viewing_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='server_table_columns',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]