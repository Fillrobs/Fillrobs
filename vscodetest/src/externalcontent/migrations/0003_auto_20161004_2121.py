# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('externalcontent', '0002_auto_20160829_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='environments',
            field=models.ManyToManyField(related_name='applications', to='infrastructure.Environment', blank=True),
        ),
        migrations.AlterField(
            model_name='application',
            name='os_builds',
            field=models.ManyToManyField(to='externalcontent.OSBuild', verbose_name='OS builds', blank=True),
        ),
        migrations.AlterField(
            model_name='osbuild',
            name='environments',
            field=models.ManyToManyField(related_name='os_builds', to='infrastructure.Environment', blank=True),
        ),
        migrations.AlterField(
            model_name='osbuild',
            name='os_versions',
            field=models.ManyToManyField(to='externalcontent.OSVersion', verbose_name='OS versions', blank=True),
        ),
        migrations.AlterField(
            model_name='osbuildattribute',
            name='custom_field_values',
            field=models.ManyToManyField(to='orders.CustomFieldValue', blank=True),
        ),
    ]
