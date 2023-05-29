# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def set_real_type(obj, ContentType):
    """Replacement for HasSubModelsMixin, which can't be used in migrations."""

    # Simplified version of ContentType.objects.get_for_model
    model = type(obj)
    ct = ContentType.objects.get(
        app_label=model._meta.app_label, model=model._meta.model_name)

    obj.real_type = ct
    obj.save()


def change_vmware_datastore_from_str_to_stor(apps, schema_editor):
    CustomField = apps.get_model('infrastructure', 'customfield')
    CustomFieldValue = apps.get_model('orders', 'customfieldvalue')
    VmwareDatastore = apps.get_model('vmware', 'vmwaredatastore')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    try:
        cf = CustomField.objects.get(name='vmware_datastore')
    except CustomField.DoesNotExist:
        # No vmware_datastore cf exists, no data changes required
        return

    cf.type = "STOR"
    cf.save()

    # First, change all CFVs to datastores without resource handlers
    cfvs = CustomFieldValue.objects.filter(field=cf)
    for cfv in cfvs:
        ds, _ = VmwareDatastore.objects.get_or_create(
            name=cfv.str_value, resource_handler=None)
        set_real_type(ds, ContentType)
        cfv.str_value = None
        cfv.int_value = ds.id
        cfv.save()

    # For any CFVs in environments, create a new datastore with the correct
    # resource handler and a new CFV for it.
    envs = cf.environment_set.all()
    for env in envs:
        rh = env.resource_handler
        cfvs = env.custom_field_options.filter(field=cf)
        for cfv in cfvs:
            # Can't use cfv.value in a migration, get the datastore manually
            old_ds = VmwareDatastore.objects.get(id=cfv.int_value)
            new_ds, _ = VmwareDatastore.objects.get_or_create(
                name=old_ds.name, resource_handler=rh)
            set_real_type(new_ds, ContentType)
            new_cfv, _ = CustomFieldValue.objects.get_or_create(
                field=cf, int_value=new_ds.id)
            env.custom_field_options.remove(cfv)
            env.custom_field_options.add(new_cfv)


def change_vmware_datastore_from_stor_to_str(apps, schema_editor):
    """Reverse migration"""
    CustomField = apps.get_model('infrastructure', 'customfield')
    CustomFieldValue = apps.get_model('orders', 'customfieldvalue')
    VmwareDatastore = apps.get_model('vmware', 'vmwaredatastore')

    try:
        cf = CustomField.objects.get(name='vmware_datastore')
    except CustomField.DoesNotExist:
        # No vmware_datastore cf exists, no data changes required
        return

    cf.type = "STR"
    cf.save()

    for cfv in CustomFieldValue.objects.filter(field=cf):
        ds = VmwareDatastore.objects.get(id=cfv.int_value)
        cfv.str_value = ds.name
        cfv.int_value = None
        cfv.save()


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
        ('vmware', '0007_remove_datastore_field'),
    ]

    operations = [
        migrations.RunPython(
            code=change_vmware_datastore_from_str_to_stor,
            reverse_code=change_vmware_datastore_from_stor_to_str),
    ]
