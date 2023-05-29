# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licenses', '0002_auto_20160901_2348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='licensepool',
            name='applications',
            field=models.ManyToManyField(to='externalcontent.Application', blank=True),
        ),
        migrations.AlterField(
            model_name='licensepool',
            name='os_builds',
            field=models.ManyToManyField(to='externalcontent.OSBuild', blank=True),
        ),
    ]
