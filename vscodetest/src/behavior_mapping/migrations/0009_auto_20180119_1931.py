# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-19 19:31
from __future__ import unicode_literals

import behavior_mapping.models
from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('behavior_mapping', '0008_auto_20180119_1912'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='customfieldmapping',
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('global_mappings', behavior_mapping.models.GlobalMappingsManager()),
                ('global_mappings_with_defaults', behavior_mapping.models.GlobalMappingsWithDefaultsManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='preconfigurationmapping',
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('global_mappings', behavior_mapping.models.GlobalMappingsManager()),
                ('global_mappings_with_defaults', behavior_mapping.models.GlobalMappingsWithDefaultsManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='resourcepoolmapping',
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('global_mappings', behavior_mapping.models.GlobalMappingsManager()),
                ('global_mappings_with_defaults', behavior_mapping.models.GlobalMappingsWithDefaultsManager()),
            ],
        ),
    ]
