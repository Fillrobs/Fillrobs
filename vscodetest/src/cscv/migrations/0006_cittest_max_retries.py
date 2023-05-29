# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('cscv', '0005_change_verbose_name_to_labels'),
    ]

    operations = [
        migrations.AddField(
            model_name='cittest',
            name='max_retries',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=True,
        ),
    ]
