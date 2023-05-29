# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0002_auto_20160901_2348'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalpreferences',
            name='allow_exceeding_quotas',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
