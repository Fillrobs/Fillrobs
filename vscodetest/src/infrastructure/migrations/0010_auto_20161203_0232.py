# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0009_serverstats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preconfiguration',
            name='name',
            field=models.CharField(help_text='Alphanumeric characters, starting with a letter, with optional underscores.', unique=True, max_length=100),
            preserve_default=True,
        ),
    ]
