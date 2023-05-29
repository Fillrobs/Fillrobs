# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('provisionengines', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='provisionengine',
            name='custom_fields',
            field=models.ManyToManyField(to='infrastructure.CustomField', blank=True),
        ),
    ]
