# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-04 23:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gcp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gcpnetwork',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='networks', to='gcp.GCPProject'),
        ),
    ]