# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gce', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gcehandler',
            name='networks',
            field=models.ManyToManyField(to='resourcehandlers.ResourceNetwork', blank=True),
        ),
        migrations.AlterField(
            model_name='gcehandler',
            name='os_build_attributes',
            field=models.ManyToManyField(to='libcloudhandler.LibcloudImage', blank=True),
        ),
    ]
