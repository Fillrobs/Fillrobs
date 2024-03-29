# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-06-06 11:23
from __future__ import unicode_literals

import cb_secrets.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('externalcontent', '0012_duplicate_osbas_in_multiple_rhs'),
        ('resourcehandlers', '0012_auto_20190501_1815'),
        ('utilities', '0062_merge_20190423_2120'),
        ('infrastructure', '0039_auto_20190503_2313'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlibabaImage',
            fields=[
                ('osbuildattribute_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='externalcontent.OSBuildAttribute')),
                ('image_id', models.CharField(max_length=256)),
            ],
            options={
                'abstract': False,
            },
            bases=('externalcontent.osbuildattribute',),
        ),
        migrations.CreateModel(
            name='AlibabaResourceHandler',
            fields=[
                ('resourcehandler_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceHandler')),
                ('region', models.CharField(max_length=30)),
                ('access_key', models.CharField(max_length=20)),
                ('access_key_secret', cb_secrets.fields.EncryptedPasswordField(max_length=40)),
                ('connection_info', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='utilities.ConnectionInfo')),
            ],
            options={
                'verbose_name': 'Alibaba Cloud resource handler',
                'abstract': False,
            },
            bases=('resourcehandlers.resourcehandler',),
        ),
        migrations.CreateModel(
            name='AlibabaServerInfo',
            fields=[
                ('server', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='infrastructure.Server')),
                ('zone', models.CharField(max_length=20)),
                ('security_group', models.CharField(max_length=50)),
                ('instance_type', models.CharField(max_length=20)),
                ('keypair_name', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AlibabaVSwitch',
            fields=[
                ('resourcenetwork_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resourcehandlers.ResourceNetwork')),
                ('cidr_block', models.CharField(max_length=30)),
            ],
            options={
                'abstract': False,
            },
            bases=('resourcehandlers.resourcenetwork',),
        ),
        migrations.AddField(
            model_name='alibabaresourcehandler',
            name='networks',
            field=models.ManyToManyField(blank=True, to='alibaba.AlibabaVSwitch'),
        ),
    ]
