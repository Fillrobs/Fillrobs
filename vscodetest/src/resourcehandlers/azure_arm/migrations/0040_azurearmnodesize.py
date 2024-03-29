# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-29 13:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('azure_arm', '0039_auto_20190102_1747'),
    ]

    operations = [
        migrations.CreateModel(
            name='AzureARMNodeSize',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('node_size', models.CharField(max_length=100)),
                ('arm_server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='node_size', to='azure_arm.AzureARMServerInfo')),
            ],
        ),
    ]
