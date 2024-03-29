# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-15 14:24
from __future__ import unicode_literals

from django.db import migrations


def update_redirect_for_service_actions_urls(apps, schema_editor):
    """
    Sinces the URLs that formerly included service_actions have been
    changed to the new resource_actions, if the "default redirect"
    miscellaneous setting is set to a URL that has changed, update it
    accordingly.
    """
    GlobalPreferences = apps.get_model("utilities", "GlobalPreferences")

    gp = GlobalPreferences.objects.first()  # There should only be 1, if any
    if gp:
        gp.default_redirect = gp.default_redirect.replace(
            '/service_actions/', '/resource_actions/')
        gp.save()


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0032_change_default_redirect_for_services_urls_20180110_2001'),
    ]

    operations = [
        migrations.RunPython(update_redirect_for_service_actions_urls, migrations.RunPython.noop),
    ]
