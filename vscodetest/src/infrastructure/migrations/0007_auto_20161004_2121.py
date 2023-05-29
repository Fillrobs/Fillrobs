# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0006_customfield_show_as_attribute'),
    ]

    operations = [
        migrations.AlterField(
            model_name='environment',
            name='custom_field_options',
            field=models.ManyToManyField(to='orders.CustomFieldValue', blank=True),
        ),
        migrations.AlterField(
            model_name='environment',
            name='custom_fields',
            field=models.ManyToManyField(to='infrastructure.CustomField', blank=True),
        ),
        migrations.AlterField(
            model_name='environment',
            name='groups_served',
            field=models.ManyToManyField(to='accounts.Group', blank=True),
        ),
        migrations.AlterField(
            model_name='environment',
            name='preconfiguration_options',
            field=models.ManyToManyField(to='orders.PreconfigurationValueSet', blank=True),
        ),
        migrations.AlterField(
            model_name='environment',
            name='preconfigurations',
            field=models.ManyToManyField(to='infrastructure.Preconfiguration', blank=True),
        ),
        migrations.AlterField(
            model_name='preconfiguration',
            name='custom_fields',
            field=models.ManyToManyField(to='infrastructure.CustomField', blank=True),
        ),
        migrations.AlterField(
            model_name='resourcepool',
            name='custom_fields',
            field=models.ManyToManyField(to='infrastructure.CustomField', verbose_name='Provides Parameters', blank=True),
        ),
        migrations.AlterField(
            model_name='resourcepoolvalueset',
            name='applications',
            field=models.ManyToManyField(to='externalcontent.Application', blank=True),
        ),
        migrations.AlterField(
            model_name='resourcepoolvalueset',
            name='custom_field_values',
            field=models.ManyToManyField(to='orders.CustomFieldValue', blank=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='applications',
            field=models.ManyToManyField(to='externalcontent.Application', blank=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='custom_field_values',
            field=models.ManyToManyField(to='orders.CustomFieldValue', blank=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='jobs',
            field=models.ManyToManyField(to='jobs.Job', blank=True),
        ),
    ]
