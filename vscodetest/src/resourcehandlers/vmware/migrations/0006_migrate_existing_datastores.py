"""
Populate the disk_storage column with VmwareDatastores created using data from
the old datastore column. The old column will be removed in the next migration.
"""
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import apps
from django.contrib.contenttypes.management import create_contenttypes
from django.db import migrations


def update_all_contenttypes(**kwargs):
    # This solution was cribbed from:
    # http://stackoverflow.com/questions/29550102/importerror-cannot-import-name-update-all-contenttypes
    for app_config in apps.get_app_configs():
        create_contenttypes(app_config, **kwargs)


def populate_disk_storage_from_datastore(apps, schema_editor):
    """
    Create VmwareDatastore objects for each datastore string.

    We set the VmwareDatastore's real_type here because the custom save() logic
    in HasSubModelsMixin is not applied inside a Django migration.
    """
    VmwareDisk = apps.get_model('vmware', 'VmwareDisk')
    VmwareDatastore = apps.get_model('vmware', 'VmwareDatastore')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    # Update all ContentTypes before getting the VmwareDatastore contenttype.
    # Normally this is done in the post_migrate signal, but we might be in the
    # same migrate command as the schema migration to create VmwareDatastore so
    # the post_migrate signal may not have run yet.
    update_all_contenttypes(interactive=False)
    contenttype = ContentType.objects.get(
        app_label=VmwareDatastore._meta.app_label,
        model=VmwareDatastore._meta.model_name
    )
    for disk in VmwareDisk.objects.all():
        rh = disk.server.resource_handler if disk.server else None
        datastore, _ = VmwareDatastore.objects.get_or_create(
            name=disk.datastore, resource_handler=rh, real_type=contenttype)
        disk.disk_storage = datastore
        disk.save()


def populate_datastore_from_disk_storage(apps, schema_editor):
    """Reverse data migration"""
    VmwareDisk = apps.get_model('vmware', 'VmwareDisk')
    for disk in VmwareDisk.objects.all():
        disk.datastore = disk.disk_storage.name
        disk.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('vmware', '0005_vmwaredatastore'),
    ]

    operations = [
        migrations.RunPython(
            code=populate_disk_storage_from_datastore,
            reverse_code=populate_datastore_from_disk_storage
        ),
    ]
