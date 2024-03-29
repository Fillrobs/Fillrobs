# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-09-25 23:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JobEngineWorker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pid', models.PositiveIntegerField(blank=True, null=True)),
                ('hostname', models.CharField(blank=True, default='', max_length=1024)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Time created')),
                ('updated_date', models.DateTimeField(auto_now=True, null=True, verbose_name='Time updated')),
            ],
        ),
    ]
