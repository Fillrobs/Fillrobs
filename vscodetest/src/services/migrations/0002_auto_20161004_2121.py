# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='attributes',
            field=models.ManyToManyField(to='orders.CustomFieldValue', blank=True),
        ),
        migrations.AlterField(
            model_name='service',
            name='jobs',
            field=models.ManyToManyField(to='jobs.Job', blank=True),
        ),
    ]
