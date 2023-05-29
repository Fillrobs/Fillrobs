# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resourcehandlers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcehandler',
            name='custom_fields',
            field=models.ManyToManyField(to='infrastructure.CustomField', blank=True),
        ),
        migrations.AlterField(
            model_name='resourcenetwork',
            name='custom_field_values',
            field=models.ManyToManyField(to='orders.CustomFieldValue', blank=True),
        ),
    ]
