# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import quota.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('orders', '0001_initial'),
        ('infrastructure', '0002_serverexpireparameters_servernetworkcard_serversnapshot'),
        ('accounts', '0002_auto_20160829_2059'),
        ('quota', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='custom_field_options',
            field=models.ManyToManyField(to='orders.CustomFieldValue', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='custom_fields',
            field=models.ManyToManyField(to='infrastructure.CustomField', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='environments',
            field=models.ManyToManyField(help_text='An empty list means the env will be available to all environments (unconstrained)', to='infrastructure.Environment', null=True, verbose_name='Available Environments', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='inherited_environments',
            field=models.ManyToManyField(related_name='groups_served_by_inheritance', null=True, verbose_name='Inherited Environments', to='infrastructure.Environment', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='accounts.Group', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='preconfiguration_options',
            field=models.ManyToManyField(to='orders.PreconfigurationValueSet', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='preconfigurations',
            field=models.ManyToManyField(to='infrastructure.Preconfiguration', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='quota_set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=quota.models.create_empty_quotaset, to='quota.ServerQuotaSet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='requestors',
            field=models.ManyToManyField(related_name='requestors', to='accounts.UserProfile', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='resource_admins',
            field=models.ManyToManyField(related_name='resource_admins', to='accounts.UserProfile', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='type',
            field=models.ForeignKey(to='accounts.GroupType', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='user_admins',
            field=models.ManyToManyField(related_name='user_admins', verbose_name='Group Admins', to='accounts.UserProfile', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='viewers',
            field=models.ManyToManyField(related_name='viewers', to='accounts.UserProfile', blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='group',
            unique_together=set([('name', 'parent')]),
        ),
    ]
