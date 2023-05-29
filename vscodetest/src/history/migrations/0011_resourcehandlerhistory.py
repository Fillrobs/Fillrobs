# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-09 13:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resourcehandlers', '0009_auto_20171212_1729'),
        ('history', '0010_auto_20180202_1944'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResourceHandlerHistory',
            fields=[
                ('historymodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='history.HistoryModel')),
                ('resource_handler', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resourcehandlers.ResourceHandler')),
            ],
            options={
                'abstract': False,
            },
            bases=('history.historymodel',),
        ),
    ]