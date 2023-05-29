# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0007_auto_20161004_2121'),
        ('azure_arm', '0003_auto_20161004_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='AzureARMDisk',
            fields=[
                ('disk_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='infrastructure.Disk', on_delete=models.CASCADE)),
                ('storage_account', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('infrastructure.disk',),
        ),
    ]
