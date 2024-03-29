# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-03 19:15
from __future__ import unicode_literals

from django.db import migrations


PERMISSIONS = [
    {
        'name': 'job.view',
        'label': 'View Jobs',
        'description': ''
    },
    {
        'name': 'job.cancel',
        'label': 'Cancel Jobs',
        'description': 'Allows the user to cancel jobs in progress.'
    },
    {
        'name': 'job.rerun',
        'label': 'Re-run Jobs',
        'description': 'Allows the user to re-run failed jobs.'
    },
]

ROLE = {
    'name': 'job_owner',
    'label': 'Job Owner',
    'description': 'Permissions that are granted to owners of jobs',
    'assignable_to_users': False,
}


def create_job_owners_without_logs(apps, schema_editor):
    """
    If restrict_job_logs_to_admins is True, then create a custom Job Owner
    role without the view_logs permission.

    If False, do nothing here. The role will be created by cb_minimal.
    """
    GlobalPreferences = apps.get_model('utilities', 'GlobalPreferences')
    Role = apps.get_model('accounts', 'Role')
    CBPermission = apps.get_model('accounts', 'CBPermission')

    gp = GlobalPreferences.objects.first()
    if gp and gp.restrict_job_logs_to_admins:
        cbperms = []
        for perm_dict in PERMISSIONS:
            cbperm, _ = CBPermission.objects.get_or_create(
                name=perm_dict['name'], defaults=perm_dict)
            cbperms.append(cbperm)

        role, _ = Role.objects.get_or_create(name=ROLE['name'], defaults=ROLE)
        role.permissions.add(*cbperms)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_migrate_existing_roles'),
        ('utilities', '0015_globalpreferences_restrict_job_logs_to_admins'),
    ]

    operations = [
        migrations.RunPython(create_job_owners_without_logs)
    ]
