# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0007_auto_20161021_1441'),
        ('hyperv', '0005_hypervresourcehandler_networks'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hypervresourcehandler',
            name='server',
        ),
        migrations.AddField(
            model_name='hypervresourcehandler',
            name='connection_info',
            field=models.ForeignKey(to='utilities.ConnectionInfo', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
    ]
