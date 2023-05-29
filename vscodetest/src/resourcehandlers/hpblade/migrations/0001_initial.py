# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resourcehandlers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HPBladeOnboardAdminHandler',
            fields=[
                ('resourcehandler_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceHandler', on_delete=models.CASCADE)),
                ('ignore_server_on', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'HP Blade OA resource handler',
            },
            bases=('resourcehandlers.resourcehandler',),
        ),
        migrations.CreateModel(
            name='VConnectNetwork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('network', models.CharField(max_length=50)),
                ('vlan', models.IntegerField(null=True, blank=True)),
                ('uplink', models.CharField(max_length=50)),
                ('poweron_stage', models.CharField(default='VM_CREATION', max_length=18, choices=[('VM_CREATION', 'On VM Creation'), ('POST_OS_INSTALL', 'Post OS Installation'), ('POST_APP_REMED', 'Post Application Remediation'), ('NONE', 'Manual Poweron')])),
            ],
            options={
                'verbose_name': 'VConnect network',
            },
            bases=(models.Model,),
        ),
    ]
