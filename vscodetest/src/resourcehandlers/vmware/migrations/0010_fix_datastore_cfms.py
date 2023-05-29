# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def fix_datastore_cfms(apps, schema_editor):
    VmwareDatastore = apps.get_model('vmware', 'VmwareDatastore')
    CustomFieldValue = apps.get_model('orders', 'CustomFieldValue')
    CustomFieldMapping = apps.get_model('behavior_mapping', 'CustomFieldMapping')

    dummy_datastores = VmwareDatastore.objects.filter(resource_handler=None)
    for datastore in dummy_datastores:
        cfvs = CustomFieldValue.objects.filter(field__name='vmware_datastore',
                                               int_value=datastore.id)
        for cfv in cfvs:
            # Change CFM options to use non-dummy datastores
            cfms_with_envs = cfv.customfieldmapping_set.exclude(environment=None)
            for cfm in cfms_with_envs:
                new_datastore, _ = VmwareDatastore.objects.get_or_create(
                    name=datastore.name,
                    resource_handler=cfm.environment.resource_handler,
                    real_type=datastore.real_type)
                new_cfv, _ = CustomFieldValue.objects.get_or_create(
                    field=cfv.field,
                    int_value=new_datastore.id)
                cfm.options.remove(cfv)
                cfm.options.add(new_cfv)

            # Change CFM defaults to use non-dummy datastores
            cfms_with_envs = CustomFieldMapping.objects.filter(default=cfv).exclude(environment=None)
            for cfm in cfms_with_envs:
                new_datastore, _ = VmwareDatastore.objects.get_or_create(
                    name=datastore.name,
                    resource_handler=cfm.environment.resource_handler,
                    real_type=datastore.real_type)
                new_cfv, _ = CustomFieldValue.objects.get_or_create(
                    field=cfv.field,
                    int_value=new_datastore.id)
                cfm.default = new_cfv
                cfm.save()


class Migration(migrations.Migration):

    dependencies = [
        ('behavior_mapping', '0002_auto_20160829_2059'),
        ('vmware', '0009_fix_psoi_datastore_cfvs'),
    ]

    operations = [
        migrations.RunPython(fix_datastore_cfms)
    ]
