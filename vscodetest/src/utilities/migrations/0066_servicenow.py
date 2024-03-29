# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-16 22:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utilities', '0065_auto_20190618_2305'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceNow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('connection_info', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='utilities.ConnectionInfo', verbose_name='Connection Info')),
            ],
        ),
    ]
