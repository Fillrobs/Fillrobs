# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-25 21:01
from __future__ import unicode_literals

from django.db import migrations


def remove_param(apps, schema_editor):
    CustomField = apps.get_model('infrastructure', 'CustomField')
    cf = CustomField.objects.filter(name='knife_bootstrap_additional_args').first()
    if cf:
        cf.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('chef', '0006_auto_20170523_0024'),
    ]

    operations = [
        migrations.RunPython(remove_param),
    ]