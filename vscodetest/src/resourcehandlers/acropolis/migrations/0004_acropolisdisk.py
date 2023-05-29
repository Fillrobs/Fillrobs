# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-16 21:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0033_auto_20180508_1222'),
        ('acropolis', '0003_auto_20180503_1800'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcropolisDisk',
            fields=[
                ('disk_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='infrastructure.Disk')),
                ('adapter_type', models.CharField(max_length=255)),
                ('device_index', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('infrastructure.disk',),
        ),
    ]