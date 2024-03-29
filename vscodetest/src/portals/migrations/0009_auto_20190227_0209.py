# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-02-27 02:09
from __future__ import unicode_literals

from django.db import migrations


def copy_top_banner_to_login_banner(apps, schema_editor):
    """
    CB used to have one field for custom banner that was used in two places (above the nav bar & on the login page). The previous migration splits them into two fields, this one copies the pre-existing value from custom_banner to login_banner to preserve the previous behavior.
    """
    PortalConfig = apps.get_model('portals', 'PortalConfig')
    for portal_config in PortalConfig.objects.all():
        portal_config.login_banner = portal_config.custom_banner
        portal_config.save()


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0008_portalconfig_login_banner'),
    ]

    operations = [
        migrations.RunPython(copy_top_banner_to_login_banner),
    ]
