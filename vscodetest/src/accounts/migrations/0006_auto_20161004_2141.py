# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20161004_2121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='custom_field_options',
            field=models.ManyToManyField(to='orders.CustomFieldValue', blank=True),
        ),
    ]
