# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-08 18:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0001_initial'),
        ('history', '0014_auto_20190111_0124'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlertHistory',
            fields=[
                ('historymodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='history.HistoryModel')),
                ('category', models.CharField(default='', help_text='The category provided for the alert', max_length=512, verbose_name="Alert's Category")),
                ('message', models.CharField(default='', help_text='The message provided for the alert', max_length=512, verbose_name="Alert's Message")),
                ('alert_channels', models.ManyToManyField(to='alerts.AlertChannel')),
            ],
            options={
                'abstract': False,
            },
            bases=('history.historymodel',),
        ),
    ]
