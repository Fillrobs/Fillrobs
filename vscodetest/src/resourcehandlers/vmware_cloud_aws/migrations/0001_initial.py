# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-12-18 15:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('vmware', '0018_remove_vsphereresourcehandler_clone_tmpl_timeout'),
    ]

    operations = [
        migrations.CreateModel(
            name='VMCAWSHandler',
            fields=[
                ('vsphereresourcehandler_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='vmware.VsphereResourceHandler')),
                ('api_token', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'VMC on AWS resource handler',
                'abstract': False,
            },
            bases=('vmware.vsphereresourcehandler',),
        ),
    ]
