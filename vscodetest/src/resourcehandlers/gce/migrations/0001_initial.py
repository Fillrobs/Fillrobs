# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resourcehandlers', '0001_initial'),
        ('libcloudhandler', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GCEHandler',
            fields=[
                ('resourcehandler_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceHandler', on_delete=models.CASCADE)),
                ('project', models.CharField(max_length=100)),
                ('networks', models.ManyToManyField(to='resourcehandlers.ResourceNetwork', null=True, blank=True)),
                ('os_build_attributes', models.ManyToManyField(to='libcloudhandler.LibcloudImage', null=True, blank=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Libcloud resource handler',
            },
            bases=('resourcehandlers.resourcehandler',),
        ),
    ]
