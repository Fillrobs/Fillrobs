# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0005_auto_20160901_2125'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobparameters',
            name='scheduled_time',
            field=models.DateTimeField(null=True, verbose_name='Time when job can start', blank=True),
            preserve_default=True,
        ),
    ]
