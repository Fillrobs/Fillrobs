# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def update_catalog_urls(apps, schema_editor):
    """
    Since the URLs for the Catalog have been changed from including
    /service_catalog/ to /catalog/, update any bookmarks that may be holding the
    old version of a Catalog URL.
    """
    Bookmark = apps.get_model("bookmarks", "Bookmark")
    catalog_bookmarks = Bookmark.objects.filter(
        page_url__contains='/service_catalog/')
    for bookmark in catalog_bookmarks:
        bookmark.page_url = bookmark.page_url.replace(
            '/service_catalog/', '/catalog/')
        bookmark.save()


class Migration(migrations.Migration):

    dependencies = [
        ('bookmarks', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_catalog_urls),
    ]
