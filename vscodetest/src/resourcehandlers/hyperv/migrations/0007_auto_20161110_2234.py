# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hyperv', '0006_auto_20161109_1955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hypervresourcehandler',
            name='connection_info',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='utilities.ConnectionInfo', null=True),
            preserve_default=True,
        ),
    ]
