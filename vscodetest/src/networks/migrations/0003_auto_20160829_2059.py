# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('servicecatalog', '0001_initial'),
        ('utilities', '0001_initial'),
        ('networks', '0002_auto_20160829_2059'),
        ('services', '0001_initial'),
        ('infrastructure', '0003_auto_20160829_2059'),
    ]

    operations = [
        migrations.AddField(
            model_name='loadbalancer',
            name='service',
            field=models.ForeignKey(to='services.Service', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='loadbalancer',
            name='service_item',
            field=models.ForeignKey(to='servicecatalog.ServiceItem', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='haproxy',
            name='server',
            field=models.ForeignKey(to='infrastructure.Server', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='f5loadbalancer',
            name='connection_info',
            field=models.ForeignKey(to='utilities.ConnectionInfo', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
    ]
