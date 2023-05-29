# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-03-04 00:44
from __future__ import unicode_literals

from django.db import migrations


def convert_subnet_cfvs(apps, schema_editor):
    """
    The subnet customfield ('sc_nic_0_subnet') has been removed, so clean
    up the cf values to be sure. These could be converted to point to the
    sc_nic_0 field, but then there might be duplicate cfvs of the same
    value.
    """
    CustomField = apps.get_model("infrastructure", "CustomField")
    CustomFieldValue = apps.get_model("orders", "CustomFieldValue")
    try:
        subnet_cf = CustomField.objects.get(name='sc_nic_0_subnet')
        for cfv in CustomFieldValue.objects.filter(field=subnet_cf):
            cfv.delete()
        subnet_cf.delete()
    except CustomField.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('gce', '0006_gceservernetworkcard'),
        ('orders', '0009_merge'),
        ('infrastructure', '0014_remove_customfield_hide_single_value'),
    ]

    operations = [
        migrations.RunPython(convert_subnet_cfvs),
    ]