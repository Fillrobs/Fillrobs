# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-27 20:49
from __future__ import unicode_literals

from django.db import migrations, models
import orders.models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0026_merge_20190627_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfieldvalue',
            name='file_value',
            field=models.FileField(blank=1, null=1, upload_to=orders.models.customfieldvalue_file_value_upload_to),
        ),
    ]
