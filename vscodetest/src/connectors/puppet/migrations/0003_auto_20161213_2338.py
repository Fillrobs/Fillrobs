# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puppet', '0002_puppetconf_version'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='puppetreport',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='puppetnode',
            unique_together=set([]),
        ),
    ]
