# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-02-23 21:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('utilities', '0014_remove_globalpreferences_allow_approver_to_edit_pending_orders'),
        ('infrastructure', '0014_remove_customfield_hide_single_value'),
        ('networks', '0003_auto_20160829_2059'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoadBalancerAppliance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('connection_info', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='utilities.ConnectionInfo')),
                ('ip_pool', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='infrastructure.ResourcePool')),
                ('technology', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='networks.LoadBalancerTechnology')),
            ],
        ),
    ]