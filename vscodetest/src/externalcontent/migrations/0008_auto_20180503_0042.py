# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-03 00:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('externalcontent', '0007_add_osbas_to_base_field_20180501_2319'),
        ('acropolis', '0002_auto_20180503_0036'),
        ('aws', '0004_auto_20180503_0036'),
        ('azure_arm', '0025_auto_20180503_0036'),
        ('gce', '0008_auto_20180503_0036'),
        ('hyperv', '0009_auto_20180503_0036'),
        ('openstack', '0006_auto_20180503_0036'),
        ('qemu', '0005_auto_20180503_0036'),
        ('slayer', '0003_auto_20180503_0036'),
        ('vmware', '0013_auto_20180503_0036'),
        ('xen', '0003_auto_20180503_0036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='osbuildattribute',
            name='resourcehandler',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='os_build_attributes', to='resourcehandlers.ResourceHandler'),
        ),
    ]