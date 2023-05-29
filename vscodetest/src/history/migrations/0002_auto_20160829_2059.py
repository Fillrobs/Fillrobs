# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('orders', '0002_auto_20160829_2059'),
        ('jobs', '0002_auto_20160829_2059'),
        ('history', '0001_initial'),
        ('accounts', '0003_auto_20160829_2059'),
        ('licenses', '0001_initial'),
        ('infrastructure', '0003_auto_20160829_2059'),
        ('contenttypes', '0001_initial'),
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicehistory',
            name='service',
            field=models.ForeignKey(to='services.Service', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='serverhistory',
            name='custom_field_values',
            field=models.ManyToManyField(to='orders.CustomFieldValue'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='serverhistory',
            name='server',
            field=models.ForeignKey(to='infrastructure.Server', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='licensepoolhistory',
            name='license_pool',
            field=models.ForeignKey(to='licenses.LicensePool', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='historymodel',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='jobs.Job', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='historymodel',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='accounts.UserProfile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='historymodel',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='groupprofiletotals',
            name='group',
            field=models.ForeignKey(to='accounts.Group', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environmenthistory',
            name='environment',
            field=models.ForeignKey(to='infrastructure.Environment', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
