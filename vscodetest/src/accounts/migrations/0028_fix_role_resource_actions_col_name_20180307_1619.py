# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-07 16:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, connection
from django.db.utils import OperationalError


def change_column_name_if_needed(apps, schema_editor):
    """
    Because of a Django migration bug, the RenameModel migration to change
    ServiceAction to ResourceAction
    (cbhooks/migrations/0030_auto_20180112_1837.py) sometimes doesn't correctly
    update the name of the serviceaction_id column in the through table for the
    M2M relationship between Roles and ResourceActions to be resourceaction_id.
    Therefore, we're adding this extra migration to do that manually when
    needed.

    If the column name is already correct, it should work fine. That's why we
    chose the option of running SQL in a python method rather than directly
    using migrations.RunSQL, so we could wrap it in a try-except.
    """
    sql_cmd = "ALTER TABLE accounts_role_resource_actions CHANGE serviceaction_id resourceaction_id int(11) NOT NULL"
    with connection.cursor() as cursor:
        try:
            cursor.execute(sql_cmd)
        except OperationalError:
            # The column name is probably already correct, so mosey along
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0027_merge_20180219_1124'),
        ('cbhooks', '0030_auto_20180112_1837'),
    ]

    if "postgresql" in settings.DATABASES["default"]["ENGINE"]:
        # This is not needed for PostgreSQL since the model has already been updated.
        operations = []
    else:
        operations = [
            migrations.RunPython(change_column_name_if_needed, migrations.RunPython.noop),
        ]
