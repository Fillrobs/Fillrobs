# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-09-11 13:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("openstack", "0008_openstackimage"),
    ]

    operations = [
        migrations.RemoveField(model_name="openstackimage", name="uuid",),
        migrations.AddField(
            model_name="openstackimage",
            name="is_bootable",
            field=models.BooleanField(default=False),
        ),
    ]
