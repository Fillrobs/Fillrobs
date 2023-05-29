# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('orders', '0002_auto_20160829_2059'),
        ('cscv', '0001_initial'),
        ('contenttypes', '0001_initial'),
        ('tags', '0001_initial'),
        ('cbhooks', '0002_auto_20160829_2059'),
    ]

    operations = [
        migrations.AddField(
            model_name='cittest',
            name='labels',
            field=taggit.managers.TaggableManager(to='tags.CloudBoltTag', through='tags.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cittest',
            name='order',
            field=models.OneToOneField(null=True, blank=True, to='orders.Order', on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cittest',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actioncittest',
            name='hook',
            field=models.ForeignKey(to='cbhooks.OrchestrationHook', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actioncittest',
            name='input_mappings',
            field=models.ManyToManyField(to='cbhooks.RunHookInputMapping'),
            preserve_default=True,
        ),
    ]
