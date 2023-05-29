# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vmware', '0006_migrate_existing_datastores'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vmwaredisk',
            name='datastore',
        ),
    ]
