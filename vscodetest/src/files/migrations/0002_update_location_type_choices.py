# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-03-16 17:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configurationfile',
            name='location_type',
            field=models.CharField(choices=[('upload', 'Upload a file'), ('url', 'Fetch from URL')], default='upload', max_length=20),
        ),
    ]
