# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-01-18 21:24
from __future__ import unicode_literals

from django.db import migrations


def update_catalog_redirect(apps, schema_editor):
    """
    Since the URLs for the Catalog have been changed from including
    /service_catalog/ to /catalog/, if the "default redirect" miscellaneous
    setting is set to a URL that includes /service_catalog/, change it to
    /catalog/.
    """
    GlobalPreferences = apps.get_model("utilities", "GlobalPreferences")
    gp = GlobalPreferences.objects.first()  # There should only be 1, if any
    if gp:
        gp.default_redirect = gp.default_redirect.replace(
            '/service_catalog/', '/catalog/')
        gp.save()


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0011_merge'),
    ]

    operations = [
        migrations.RunPython(update_catalog_redirect),
    ]