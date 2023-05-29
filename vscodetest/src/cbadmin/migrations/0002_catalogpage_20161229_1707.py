# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def remove_old_catalog_page(apps, schema_editor):
    """
    When we changed the definition of the Catalog (formerly Service Catalog)
    StaticPage in cb_minimal, it caused creation of a new StaticPage but left
    the old one around. So let's clean up the old one.
    """
    StaticPage = apps.get_model("cbadmin", "StaticPage")
    service_catalog_page = StaticPage.objects.filter(name='Service Catalog')
    for page in service_catalog_page:
        page.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cbadmin', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(remove_old_catalog_page),
    ]
