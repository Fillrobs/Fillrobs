# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libcloudhandler', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='libcloudimage',
            name='total_disk_size',
            field=models.DecimalField(help_text='Total size of all disks on this image in GB', null=True, max_digits=10, decimal_places=4, blank=True),
            preserve_default=True,
        ),
    ]
