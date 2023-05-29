# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0010_auto_20161203_0232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preconfiguration',
            name='name',
            field=models.CharField(help_text='Alphanumeric characters, starting with a letter, with optional underscores.', unique=True, max_length=100, validators=[common.validators.valid_python_identifier]),
            preserve_default=True,
        ),
    ]
