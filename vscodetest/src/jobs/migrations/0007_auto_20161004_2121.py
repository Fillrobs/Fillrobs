# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0006_jobparameters_scheduled_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deletesnapshotsparameters',
            name='snapshots',
            field=models.ManyToManyField(to='infrastructure.ServerSnapshot', blank=True),
        ),
        migrations.AlterField(
            model_name='functionaltestparameters',
            name='cittests',
            field=models.ManyToManyField(help_text='Test(s) to run', to='cscv.CITTest'),
        ),
        migrations.AlterField(
            model_name='hookparameters',
            name='servers',
            field=models.ManyToManyField(to='infrastructure.Server'),
        ),
        migrations.AlterField(
            model_name='hookparameters',
            name='services',
            field=models.ManyToManyField(to='services.Service'),
        ),
        migrations.AlterField(
            model_name='syncsvrsfrompesparameters',
            name='provision_engines',
            field=models.ManyToManyField(to='provisionengines.ProvisionEngine', blank=True),
        ),
        migrations.AlterField(
            model_name='syncvmparameters',
            name='resource_handlers',
            field=models.ManyToManyField(to='resourcehandlers.ResourceHandler', blank=True),
        ),
    ]
