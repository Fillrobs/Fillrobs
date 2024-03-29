# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-11-18 23:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cbhooks', '0063_auto_20191107_0049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hookpointaction',
            name='hook',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cbhooks.OrchestrationHook'),
        ),
        migrations.AlterField(
            model_name='recurringactionjob',
            name='hook',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cbhooks.OrchestrationHook'),
        ),
        migrations.AlterField(
            model_name='resourceaction',
            name='hook',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cbhooks.OrchestrationHook'),
        ),
        migrations.AlterField(
            model_name='serveraction',
            name='hook',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cbhooks.OrchestrationHook'),
        ),
        migrations.AlterField(
            model_name='triggerpoint',
            name='condition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cbhooks.OrchestrationHook'),
        ),
    ]
