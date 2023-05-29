# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-12 16:56
from __future__ import unicode_literals

from django.db import migrations


def set_rh_console_from_global_preference(apps, schema_editor):
    ResourceHandler = apps.get_model("resourcehandlers", "ResourceHandler")
    GlobalPreferences = apps.get_model("utilities", "GlobalPreferences")

    gp = GlobalPreferences.objects.first()  # singleton, there should only be one

    if gp:  # check if there is an object, in case this is running from the installer and there isn't one.
        # iterate over all resource handlers and set them to the boolean value of the GP.
        for rh in ResourceHandler.objects.all():
            rh.enable_console_feature = gp.enable_console_feature
            rh.save()


class Migration(migrations.Migration):

    dependencies = [
        ('resourcehandlers', '0007_resourcehandler_enable_console_feature'),
        ('utilities', '0027_globalpreferences_job_timeout')
    ]

    operations = [
        migrations.RunPython(set_rh_console_from_global_preference),
    ]
