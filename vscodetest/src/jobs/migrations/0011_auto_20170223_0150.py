# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-02-23 01:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('jobs', '0010_auto_20170130_2012'),
    ]

    operations = [
        migrations.AddField(
            model_name='recurringjob',
            name='real_type',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='recurringjob',
            name='parameters',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='jobs.JobParameters'),
        ),
    ]
