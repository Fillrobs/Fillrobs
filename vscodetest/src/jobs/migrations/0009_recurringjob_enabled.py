# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0008_auto_20161006_2151'),
    ]

    operations = [
        migrations.AddField(
            model_name='recurringjob',
            name='enabled',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
