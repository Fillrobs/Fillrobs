# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-22 23:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_installpodorderitem_custom_field_values'),
        ('behavior_mapping', '0006_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfieldmapping',
            name='options',
            field=models.ManyToManyField(blank=True, db_table='behavior_mapping_customfieldmapping_options', to='orders.CustomFieldValue'),
        ),
        migrations.RenameField(
            model_name='customfieldmapping',
            old_name='options',
            new_name='custom_field_options',
        ),
    ]
