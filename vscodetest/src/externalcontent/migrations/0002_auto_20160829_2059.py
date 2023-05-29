# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('orders', '0001_initial'),
        ('infrastructure', '0002_serverexpireparameters_servernetworkcard_serversnapshot'),
        ('contenttypes', '0001_initial'),
        ('externalcontent', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='osbuildattribute',
            name='custom_field_values',
            field=models.ManyToManyField(to='orders.CustomFieldValue', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='osbuildattribute',
            name='os_build',
            field=models.ForeignKey(verbose_name='OS build', blank=True, to='externalcontent.OSBuild', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='osbuildattribute',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='osbuild',
            name='environments',
            field=models.ManyToManyField(related_name='os_builds', null=True, to='infrastructure.Environment', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='osbuild',
            name='os_family',
            field=models.ForeignKey(related_name='os_build_set', verbose_name='OS family', blank=True, to='externalcontent.OSFamily', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='osbuild',
            name='os_versions',
            field=models.ManyToManyField(to='externalcontent.OSVersion', null=True, verbose_name='OS versions', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='application',
            name='environments',
            field=models.ManyToManyField(related_name='applications', null=True, to='infrastructure.Environment', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='application',
            name='os_builds',
            field=models.ManyToManyField(to='externalcontent.OSBuild', null=True, verbose_name='OS builds', blank=True),
            preserve_default=True,
        ),
    ]
