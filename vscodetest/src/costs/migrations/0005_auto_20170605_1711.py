# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-05 17:11
from __future__ import unicode_literals

from django.db import migrations


def set_poweroff_rates(apps, schema_editor):
    """
    poweroff rates are now in the DB and no longer magical, need to be instantiated with the same
    value as regular (poweron) rates
    """
    CustomFieldRate = apps.get_model("costs", "CustomFieldRate")
    for cfr in CustomFieldRate.objects.all():
        if cfr.custom_field.name not in ['cpu_cnt', 'mem_size']:
            cfr.poweroff_rate = cfr.rate
            cfr.save()


class Migration(migrations.Migration):

    dependencies = [
        ('costs', '0004_auto_20170602_1949'),
    ]

    operations = [
        migrations.RunPython(set_poweroff_rates, migrations.RunPython.noop),
    ]
