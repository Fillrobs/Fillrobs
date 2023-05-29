# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vmware', '0002_auto_20160901_2348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vmwareserverinfo',
            name='snapshots',
            field=models.ManyToManyField(to='infrastructure.ServerSnapshot', blank=True),
        ),
        migrations.AlterField(
            model_name='vsphereresourcehandler',
            name='networks',
            field=models.ManyToManyField(related_name='resource_handler', to='vmware.VmwareNetwork'),
        ),
        migrations.AlterField(
            model_name='vsphereresourcehandler',
            name='os_build_attributes',
            field=models.ManyToManyField(related_name='resource_handler', to='vmware.VsphereOSBuildAttribute', blank=True),
        ),
    ]
