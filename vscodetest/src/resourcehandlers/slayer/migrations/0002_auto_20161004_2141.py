# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slayer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slayerresourcehandler',
            name='networks',
            field=models.ManyToManyField(to='slayer.SlayerNetwork', blank=True),
        ),
        migrations.AlterField(
            model_name='slayerresourcehandler',
            name='os_build_attributes',
            field=models.ManyToManyField(to='slayer.SlayerOSBuildAttribute', blank=True),
        ),
    ]
