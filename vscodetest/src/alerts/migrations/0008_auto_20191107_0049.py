# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-11-07 00:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0007_auto_20190819_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alertchannel',
            name='real_type',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType'),
        ),
    ]
