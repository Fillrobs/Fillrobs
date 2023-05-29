# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('servicecatalog', '0001_initial'),
        ('services', '0001_initial'),
        ('infrastructure', '0003_auto_20160829_2059'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='services.Service', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='server',
            name='service_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='servicecatalog.ProvisionServerServiceItem', null=True),
            preserve_default=True,
        ),
    ]
