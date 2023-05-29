# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_auto_20161004_2121'),
        ('infrastructure', '0011_auto_20161213_2334'),
    ]

    operations = [
        migrations.AddField(
            model_name='resourcepoolvalueset',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='services.Service', null=True),
            preserve_default=True,
        ),
    ]
