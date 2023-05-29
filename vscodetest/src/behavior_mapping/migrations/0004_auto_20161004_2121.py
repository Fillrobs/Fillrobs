# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('behavior_mapping', '0003_sequenceditem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfieldmapping',
            name='options',
            field=models.ManyToManyField(to='orders.CustomFieldValue', blank=True),
        ),
        migrations.AlterField(
            model_name='preconfigurationmapping',
            name='options',
            field=models.ManyToManyField(to='orders.PreconfigurationValueSet'),
        ),
    ]
