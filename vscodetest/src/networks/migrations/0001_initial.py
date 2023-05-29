# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('utilities', '0001_initial'),
        ('infrastructure', '0002_serverexpireparameters_servernetworkcard_serversnapshot'),
        ('accounts', '0002_auto_20160829_2059'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoadBalancer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('dns_name', models.CharField(max_length=255)),
                ('identifier', models.CharField(help_text='identifier to tell external API what unique id to look for', max_length=255)),
                ('pool_identifier', models.CharField(help_text='ID for the Load Balancer member pool', max_length=255, null=True, blank=True)),
                ('source_port', models.PositiveIntegerField()),
                ('destination_port', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HAProxy',
            fields=[
                ('loadbalancer_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='networks.LoadBalancer', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('networks.loadbalancer',),
        ),
        migrations.CreateModel(
            name='F5LoadBalancer',
            fields=[
                ('loadbalancer_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='networks.LoadBalancer', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('networks.loadbalancer',),
        ),
        migrations.CreateModel(
            name='LoadBalancerTechnology',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name of the Load Balancer technology')),
                ('version', models.CharField(max_length=20, null=True, verbose_name='Version of the load balancer technology', blank=True)),
                ('icon_image', models.ImageField(default='', upload_to='networks/load_balancers/', blank=True, help_text='Any size. All standard image formats work, though PNGs with alpha transparency look best.', null=True)),
                ('type_slug', models.CharField(verbose_name='LB Tech identifier.  Read Only', max_length=20, editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NetscalerLoadBalancer',
            fields=[
                ('loadbalancer_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='networks.LoadBalancer', on_delete=models.CASCADE)),
                ('connection_info', models.ForeignKey(to='utilities.ConnectionInfo', null=True, on_delete=models.SET_NULL)),
            ],
            options={
                'abstract': False,
            },
            bases=('networks.loadbalancer',),
        ),
        migrations.AddField(
            model_name='loadbalancer',
            name='environment',
            field=models.ForeignKey(to='infrastructure.Environment', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='loadbalancer',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='accounts.Group', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='loadbalancer',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='accounts.UserProfile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='loadbalancer',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
    ]
