# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-09-09 16:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ipam', '0005_auto_20190710_1848'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlueCatIPAM',
            fields=[
                ('ipam_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='ipam.IPAM')),
            ],
            options={
                'abstract': False,
            },
            bases=('ipam.ipam',),
        ),
    ]
