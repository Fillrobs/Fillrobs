# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20161004_2121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='installserviceitemoptions',
            name='preconfiguration_values',
            field=models.ManyToManyField(to='orders.PreconfigurationValueSet', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='provisionserverorderitem',
            name='preconfiguration_values',
            field=models.ManyToManyField(to='orders.PreconfigurationValueSet', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='servermodorderitem',
            name='original_custom_field_values',
            field=models.ManyToManyField(related_name='mod_oi_orig_values_set', to='orders.CustomFieldValue', blank=True),
            preserve_default=True,
        ),
    ]
