# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-29 16:08
from __future__ import unicode_literals

from django.db import migrations


def remove_duplicate_grms(apps, schema_editor):
    """
    In preparation for implementing database constraints to prevent duplicate
    GroupRoleMemberships (there should only ever be one for a group, role &
    profile combination), clean up any existing duplicates so it doesn't start
    blowing up. We don't know if any exist for customers, but for those of us
    internally who have installed the reston labs objects we will likely have
    some.
    """
    GroupRoleMembership = apps.get_model('accounts', 'GroupRoleMembership')

    # For all the existing group, profile & role combinations, check if they
    # have duplicate GRMs and, if so, delete all but the first (prioritizing
    # GRMs with inheritance info if applicable)
    grm_combinations = GroupRoleMembership.objects.all().values_list(
        'group_id', 'role_id', 'profile_id')
    unique_combinations = set(grm_combinations)
    for group_id, role_id, profile_id in unique_combinations:
        grms = GroupRoleMembership.objects.filter(
            group_id=group_id, profile_id=profile_id, role_id=role_id)
        if grms.count() > 1:
            if grms.filter(group_inherited_from__isnull=False).exists():
                keep_grm = grms.filter(group_inherited_from__isnull=False).first()
            else:
                keep_grm = grms.first()
            to_delete = grms.exclude(id=keep_grm.id)
            to_delete.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0032_merge_20180508_1334'),
    ]

    operations = [
        migrations.RunPython(remove_duplicate_grms,
                             migrations.RunPython.noop),
    ]
