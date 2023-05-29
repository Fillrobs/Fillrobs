# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-01-26 17:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0013_all_boolean_fields_optional'),
        ('gce', '0005_auto_20170113_0101'),
    ]

    operations = [
        migrations.CreateModel(
            name='GCEServerNetworkCard',
            fields=[
                ('servernetworkcard_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='infrastructure.ServerNetworkCard')),
                ('subnetwork_name', models.CharField(blank=True, max_length=1024)),
            ],
            options={
                'verbose_name': 'GCE NIC',
            },
            bases=('infrastructure.servernetworkcard',),
        ),
    ]
