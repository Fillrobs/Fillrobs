# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hyperv', '0007_auto_20161110_2234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hypervresourcehandler',
            name='os_build_attributes',
            field=models.ManyToManyField(to='hyperv.HyperVImage', blank=True),
        ),
    ]
