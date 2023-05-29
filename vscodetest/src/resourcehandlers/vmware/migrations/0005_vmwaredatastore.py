# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0008_diskstorage'),
        ('vmware', '0004_set_network_to_portgroup_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='VmwareDatastore',
            fields=[
                ('diskstorage_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='infrastructure.DiskStorage', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('infrastructure.diskstorage',),
        ),
    ]
