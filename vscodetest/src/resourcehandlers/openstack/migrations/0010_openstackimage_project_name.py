# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-09-27 15:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("openstack", "0009_auto_20190911_1356"),
    ]

    operations = [
        migrations.AddField(
            model_name="openstackimage",
            name="project_name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
