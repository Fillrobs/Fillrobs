# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('jobs', '0003_auto_20160829_2059'),
        ('orders', '0002_auto_20160829_2059'),
        ('cbhooks', '0002_auto_20160829_2059'),
        ('provisionengines', '0001_initial'),
        ('resourcehandlers', '0001_initial'),
        ('orchestrationengines', '0001_initial'),
        ('contenttypes', '0001_initial'),
        ('tags', '0001_initial'),
        ('infrastructure', '0005_auto_20160829_2059'),
    ]

    operations = [
        migrations.AddField(
            model_name='functionaltestparameters',
            name='labels_to_run',
            field=taggit.managers.TaggableManager(to='tags.CloudBoltTag', through='tags.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='externaljob',
            name='engine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=1, to='provisionengines.ProvisionEngine', null=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='externaljob',
            name='handler',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=1, to='resourcehandlers.ResourceHandler', null=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='externaljob',
            name='job',
            field=models.ForeignKey(to='jobs.Job', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='externaljob',
            name='orchestrator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=1, to='orchestrationengines.OrchestrationEngine', null=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='deletesnapshotsparameters',
            name='snapshots',
            field=models.ManyToManyField(to='infrastructure.ServerSnapshot', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cfvchangeparameters',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cfvchangeparameters',
            name='hook',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='cbhooks.OrchestrationHook', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cfvchangeparameters',
            name='post_custom_field_value',
            field=models.ForeignKey(related_name='post_cfvchangeparameters_set', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='orders.CustomFieldValue', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cfvchangeparameters',
            name='pre_custom_field_value',
            field=models.ForeignKey(related_name='pre_cfvchangeparameters_set', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='orders.CustomFieldValue', null=True),
            preserve_default=True,
        ),
    ]
