# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-08-30 21:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0029_blueprintorderitem_preconfiguration_values'),
        ('infrastructure', '0044_environment_container_orchestrator'),
        ('servicecatalog', '0051_merge_20190815_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceblueprint',
            name='preconfiguration_options',
            field=models.ManyToManyField(blank=True, to='orders.PreconfigurationValueSet'),
        ),
        migrations.AddField(
            model_name='serviceblueprint',
            name='preconfigurations_for_items',
            field=models.ManyToManyField(blank=True, related_name='serviceblueprint_set_for_items', to='infrastructure.Preconfiguration'),
        ),
        migrations.AddField(
            model_name='serviceblueprint',
            name='preconfigurations_for_resource',
            field=models.ManyToManyField(blank=True, related_name='serviceblueprint_set_for_resource', to='infrastructure.Preconfiguration'),
        ),
    ]