# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('connectors', '0001_initial'),
        ('infrastructure', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='featuremap',
            name='environment',
            field=models.ForeignKey(to='infrastructure.Environment', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='featuremap',
            name='feature',
            field=models.ForeignKey(to='connectors.Feature', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='featuremap',
            unique_together=set([('environment', 'feature')]),
        ),
        migrations.AddField(
            model_name='connectorconf',
            name='connector',
            field=models.ForeignKey(to='connectors.Connector', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='connectorconf',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
    ]
