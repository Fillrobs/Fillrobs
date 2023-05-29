# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def fix_psoi_datastore_cfvs(apps, schema_editor):
    """
    The previous migration changed the value of vmware_datastore CFVs from
    strings to VmwareDatastore objects, but some of the VmwareDatastores (e.g.
    the ones on PSOIs) were dummy values with no resource handler.

    This migration changes the PSOI CFVs to use datastores with the correct
    resource handlers. This means that the correct datastore will be used when
    duplicating an order, or running a CIT test from a past order.
    """
    VmwareDatastore = apps.get_model('vmware', 'VmwareDatastore')
    CustomFieldValue = apps.get_model('orders', 'CustomFieldValue')

    dummy_datastores = VmwareDatastore.objects.filter(resource_handler=None)
    for datastore in dummy_datastores:
        cfvs = CustomFieldValue.objects.filter(field__name='vmware_datastore',
                                               int_value=datastore.id)
        for cfv in cfvs:
            # Exclude PSOIs whose environments have been deleted because
            # we don't know the resource handler they used. Without the RH, we
            # can't determine the correct VmwareDatastore for the PSOI.
            psois_with_envs = cfv.provisionserverorderitem_set.exclude(environment=None)
            for psoi in psois_with_envs:
                # We found a PSOI referencing a CFV using a dummy datastore, so
                # let's get (or create) the real datastore, get (or create) a
                # CFV using that datastore, and replace the old CFV with the
                # new one.
                new_datastore, _ = VmwareDatastore.objects.get_or_create(
                    name=datastore.name,
                    resource_handler=psoi.environment.resource_handler,
                    real_type=datastore.real_type)
                new_cfv, _ = CustomFieldValue.objects.get_or_create(
                    field=cfv.field,
                    int_value=new_datastore.id)
                psoi.custom_field_values.remove(cfv)
                psoi.custom_field_values.add(new_cfv)


class Migration(migrations.Migration):

    dependencies = [
        ('vmware', '0008_change_vmware_datastore_cf_from_str_to_stor'),
    ]

    operations = [
        migrations.RunPython(fix_psoi_datastore_cfvs)
    ]
