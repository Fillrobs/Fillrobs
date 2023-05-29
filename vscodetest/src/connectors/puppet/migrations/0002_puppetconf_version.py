# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('puppet', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='puppetconf',
            name='version',
            field=models.CharField(default='pre-4.4', max_length=10, choices=[('pre-4.4', 'Before 4.4'), ('post-4.4', '4.4+')]),
            preserve_default=True,
        ),
    ]
