# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servicecatalog', '0003_auto_20161004_2121'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceblueprint',
            name='create_service',
            field=models.BooleanField(default=True, help_text='Specify whether ordering the Blueprint should create a service or simply provision any included servers.'),
            preserve_default=True,
        ),
    ]
