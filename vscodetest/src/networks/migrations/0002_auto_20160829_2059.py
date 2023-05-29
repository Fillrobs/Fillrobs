# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('resourcehandlers', '0001_initial'),
        ('networks', '0001_initial'),
        ('infrastructure', '0003_auto_20160829_2059'),
    ]

    operations = [
        migrations.AddField(
            model_name='loadbalancer',
            name='resource_handler',
            field=models.ForeignKey(to='resourcehandlers.ResourceHandler', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='loadbalancer',
            name='servers',
            field=models.ManyToManyField(to='infrastructure.Server'),
            preserve_default=True,
        ),
    ]
