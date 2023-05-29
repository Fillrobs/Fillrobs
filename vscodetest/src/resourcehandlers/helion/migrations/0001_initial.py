# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openstack', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HelionHandler',
            fields=[
                ('openstackhandler_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='openstack.OpenStackHandler', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Helion Resource Handler',
            },
            bases=('openstack.openstackhandler',),
        ),
    ]
