# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-22 22:56
from __future__ import unicode_literals

from django.db import migrations


# Copied from cb_minimal, because migrations run first
CF_DICT = {
    'name': 'key_name',
    'label': 'Key pair name',
    'type': 'STR',
    'required': True,
    'description': ("Name of a key pair defined in this resource "
                    "handler. Stored on an instance during launch to "
                    "enable secure key-based access.")
}


def move_cfvs_and_delete_cf(apps, schema_editor):
    """
    Do the steps necessary to move from using the ssh_keys CF to the key_name
    CF. Depending on the situation, may include copying CFV values and deleting
    the old CF.
    """
    CustomField = apps.get_model('infrastructure', 'CustomField')
    CustomFieldValue = apps.get_model('orders', 'CustomFieldValue')
    # If they don't have the ssh_keys CF, we don't need to do anything
    old_cf = CustomField.objects.filter(name='ssh_keys')
    if not old_cf.exists():
        return
    old_cf = old_cf.first()

    new_cf, _ = CustomField.objects.get_or_create(
        name=CF_DICT['name'], defaults=CF_DICT)
    # Make sure the new CF is used in places where old was
    old_cf.customfieldmapping_set.all().update(
        custom_field=new_cf)
    for env in old_cf.environment_set.all():
        env.custom_fields.remove(old_cf)
        env.custom_fields.add(new_cf)
    for pc in old_cf.preconfiguration_set.all():
        pc.custom_fields.remove(old_cf)
        pc.custom_fields.add(new_cf)

    old_cfvs = CustomFieldValue.objects.filter(field=old_cf)
    for old_cfv in old_cfvs:
        new_cfv, _ = CustomFieldValue.objects.get_or_create(
            field=new_cf, str_value=old_cfv.str_value)
        # Add the new CFV to the places where the old CFV was used, trying
        # to cover the realistic places where it might have been used as
        # completely as possible
        old_cfv.cfms_using_this_as_default_value.all().update(
            default=new_cfv)
        for cfm in old_cfv.customfieldmapping_set.all():
            cfm.options.remove(old_cfv)
            cfm.options.add(new_cfv)
        for env in old_cfv.environment_set.all():
            env.custom_field_options.remove(old_cfv)
            env.custom_field_options.add(new_cfv)
        for osba in old_cfv.osbuildattribute_set.all():
            osba.custom_field_values.remove(old_cfv)
            osba.custom_field_values.add(new_cfv)
        for pcvs in old_cfv.preconfigurationvalueset_set.all():
            pcvs.custom_field_values.remove(old_cfv)
            pcvs.custom_field_values.add(new_cfv)
        for psoi in old_cfv.provisionserverorderitem_set.all():
            psoi.custom_field_values.remove(old_cfv)
            psoi.custom_field_values.add(new_cfv)
        for isio in old_cfv.installserviceitemoptions_set.all():
            isio.custom_field_values.remove(old_cfv)
            isio.custom_field_values.add(new_cfv)
        for svr in old_cfv.server_set.all():
            svr.custom_field_values.remove(old_cfv)
            svr.custom_field_values.add(new_cfv)
        old_cfv.delete()

    old_cf.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0015_auto_20170505_0022'),
        ('orders', '0011_installpodorderitem_custom_field_values'),
    ]

    operations = [
        migrations.RunPython(move_cfvs_and_delete_cf),
    ]
