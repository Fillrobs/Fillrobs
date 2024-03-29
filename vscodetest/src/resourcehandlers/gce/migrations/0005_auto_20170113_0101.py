# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-01-13 01:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resourcehandlers', '0002_auto_20161004_2121'),
        ('gce', '0004_gcenetwork_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='GCESubnetwork',
            fields=[
                ('resourcenetwork_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceNetwork')),
                ('cidr_block', models.CharField(blank=True, max_length=30)),
                ('region', models.CharField(max_length=128)),
                ('parent_network', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subnetworks', to='gce.GCENetwork')),
            ],
            options={
                'verbose_name': 'GCE Subnetwork',
            },
            bases=('resourcehandlers.resourcenetwork',),
        ),
        migrations.AddField(
            model_name='gcehandler',
            name='subnetworks',
            field=models.ManyToManyField(blank=True, related_name='subnetwork_gce_handlers', to='resourcehandlers.ResourceNetwork'),
        ),
    ]
