# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('infrastructure', '0001_initial'),
        ('externalcontent', '0001_initial'),
        ('licenses', '0001_initial'),
        ('costs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='osbuildrate',
            name='environment',
            field=models.ForeignKey(blank=True, to='infrastructure.Environment', help_text='If not set, this rate will apply to all environments.', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='osbuildrate',
            name='os_build',
            field=models.ForeignKey(to='externalcontent.OSBuild', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='osbuildrate',
            unique_together=set([('environment', 'os_build')]),
        ),
        migrations.AddField(
            model_name='licenserate',
            name='environment',
            field=models.ForeignKey(blank=True, to='infrastructure.Environment', help_text='If not set, this rate will apply to all environments.', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='licenserate',
            name='license_pool',
            field=models.ForeignKey(to='licenses.LicensePool', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='licenserate',
            unique_together=set([('environment', 'license_pool')]),
        ),
        migrations.AddField(
            model_name='customfieldrate',
            name='custom_field',
            field=models.ForeignKey(to='infrastructure.CustomField', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customfieldrate',
            name='environment',
            field=models.ForeignKey(blank=True, to='infrastructure.Environment', help_text='If not set, this rate will apply to all environments.', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='customfieldrate',
            unique_together=set([('environment', 'custom_field')]),
        ),
        migrations.AddField(
            model_name='applicationrate',
            name='application',
            field=models.ForeignKey(to='externalcontent.Application', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='applicationrate',
            name='environment',
            field=models.ForeignKey(blank=True, to='infrastructure.Environment', help_text='If not set, this rate will apply to all environments.', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='applicationrate',
            unique_together=set([('environment', 'application')]),
        ),
    ]
