# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NSXEdge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('object_id', models.CharField(max_length=50)),
                ('edge_type', models.CharField(max_length=5, choices=[('LDR', 'Logical Distributed Router'), ('ESG', 'Edge Service Gateway'), ('UNK', 'Other Edge Type')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NSXEdgeConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datacenter_moid', models.CharField(max_length=100)),
                ('datastore_moid', models.CharField(max_length=100)),
                ('resource_pool_moid', models.CharField(max_length=100)),
                ('folder_moid', models.CharField(max_length=100, null=True, blank=True)),
                ('cli_username', models.CharField(default='cloudbolt', max_length=100)),
                ('cli_password', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NSXScope',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('object_id', models.CharField(max_length=50, editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
