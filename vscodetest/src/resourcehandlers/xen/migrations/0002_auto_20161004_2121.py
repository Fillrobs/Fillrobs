# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xen', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='xenresourcehandler',
            name='networks',
            field=models.ManyToManyField(to='xen.XenNetwork', blank=True),
        ),
        migrations.AlterField(
            model_name='xenresourcehandler',
            name='os_build_attributes',
            field=models.ManyToManyField(to='xen.XenOSBuildAttribute', blank=True),
        ),
    ]
