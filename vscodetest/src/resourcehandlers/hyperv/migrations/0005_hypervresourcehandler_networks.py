# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resourcehandlers', '0002_auto_20161004_2121'),
        ('hyperv', '0004_auto_20161024_1800'),
    ]

    operations = [
        migrations.AddField(
            model_name='hypervresourcehandler',
            name='networks',
            field=models.ManyToManyField(to='resourcehandlers.ResourceNetwork', blank=True),
            preserve_default=True,
        ),
    ]
