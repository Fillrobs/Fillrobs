# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-11 00:02
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, connection
from django.db.utils import OperationalError


def alter_action_time_column(apps, schema_editor):
    """
    Add fractional support for seconds to the action_time field of HistoryModel.
    https://docs.djangoproject.com/en/2.2/ref/databases/#fractional-seconds-support-for-time-and-datetime-fields
    """
    sql_cmd = "ALTER TABLE `history_historymodel` MODIFY `action_time` DATETIME(6)"
    with connection.cursor() as cursor:
        try:
            cursor.execute(sql_cmd)
        except OperationalError:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0013_merge_20180501_2027'),
    ]

    if "postgresql" in settings.DATABASES["default"]["ENGINE"]:
        # This is not needed for PostgreSQL since the model has already been updated.
        operations = []
    else:
        operations = [
            migrations.RunPython(alter_action_time_column, migrations.RunPython.noop),
        ]
