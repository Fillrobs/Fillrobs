# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import resourcehandlers.vmware.models


class Migration(migrations.Migration):

    dependencies = [
        ('vmware', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vsphereresourcehandler',
            name='virtual_folder_path',
            field=models.CharField(default='CloudBoltVMs/{{ group }}', help_text=resourcehandlers.vmware.models.vsphereresourcehandler_virtual_folder_path_help_text, max_length=100),
            preserve_default=True,
        ),
    ]
