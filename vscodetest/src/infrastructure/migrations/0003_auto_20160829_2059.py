# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('externalcontent', '0002_auto_20160829_2059'),
        ('provisionengines', '0001_initial'),
        ('resourcehandlers', '0001_initial'),
        ('orders', '0001_initial'),
        ('accounts', '0003_auto_20160829_2059'),
        ('infrastructure', '0002_serverexpireparameters_servernetworkcard_serversnapshot'),
        ('jobs', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='servernetworkcard',
            name='network',
            field=models.ForeignKey(blank=True, to='resourcehandlers.ResourceNetwork', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='servernetworkcard',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='servernetworkcard',
            name='server',
            field=models.ForeignKey(related_name='nics', to='infrastructure.Server', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='servernetworkcard',
            unique_together=set([('index', 'server')]),
        ),
        migrations.AddField(
            model_name='serverexpireparameters',
            name='servers',
            field=models.ManyToManyField(to='infrastructure.Server'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='server',
            name='applications',
            field=models.ManyToManyField(to='externalcontent.Application', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='server',
            name='custom_field_values',
            field=models.ManyToManyField(to='orders.CustomFieldValue', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='server',
            name='environment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='environment', to='infrastructure.Environment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='server',
            name='group',
            field=models.ForeignKey(to='accounts.Group', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='server',
            name='jobs',
            field=models.ManyToManyField(to='jobs.Job', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='server',
            name='os_build',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='OS Build', blank=True, to='externalcontent.OSBuild', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='server',
            name='os_family',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='OS Family', blank=True, to='externalcontent.OSFamily', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='server',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='accounts.UserProfile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='server',
            name='provision_engine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='provisionengines.ProvisionEngine', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='server',
            name='resource_handler',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='resourcehandlers.ResourceHandler', null=True),
            preserve_default=True,
        ),
    ]
