# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-12 20:40
from __future__ import unicode_literals

from django.db import migrations


def rename_server_owners(apps, schema_editor):
    """
    Rename Server Owners -> Server Owner

    Server Owners was only used for the first two alphas of 7.2, so this will
    not affect many customers.
    """
    Role = apps.get_model('accounts', 'Role')
    try:
        role = Role.objects.get(name='server_owners')
    except Role.DoesNotExist:
        return  # nothing to do
    role.name = 'server_owner'
    role.label = 'Server Owner'
    role.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_auto_20170511_2000'),
    ]

    operations = [
        migrations.RunPython(rename_server_owners),
    ]